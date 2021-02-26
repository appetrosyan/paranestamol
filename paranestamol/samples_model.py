"""This module defines the abstracListModel subclass that is used to
keep the QML model in sync with the Python back end.

"""
from matplotlib_backend_qtquick.qt_compat import QtCore
from anesthetic.samples import NestedSamples, MCMCSamples
from os.path import basename
import matplotlib.pyplot as plt
from math import ceil

from .utils import cleanupFileRoot, Legend


class ParameterModel(QtCore.QAbstractListModel):
    nameRole = QtCore.Qt.UserRole + 1000 + 0
    texRole = QtCore.Qt.UserRole + 1000 + 1
    selectedRole = QtCore.Qt.UserRole + 1000 + 2

    isEmptyChanged = QtCore.Signal()

    def _isEmpty(self):
        return self.rowCount() < 1

    isEmpty = QtCore.Property(bool, _isEmpty, notify=isEmptyChanged)

    def __init__(self, parent=None, columns=[], tex={}):
        super(ParameterModel, self).__init__(parent)
        self.names = columns
        self.tex = tex
        self.displayNames = {}

    def roleNames(self):
        roles = {
            ParameterModel.nameRole: b'name',
            ParameterModel.texRole: b'tex',
            ParameterModel.selectedRole: b'selected',
        }
        return roles

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.names)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount() and index.isValid():
            if role == ParameterModel.nameRole:
                return self.names[index.row()]
            if role == ParameterModel.texRole:
                return self.parent.tex[self.names[index.row()]]
            if role == ParameterModel.selectedRole:
                return self.names[index.row()] in self.displayNames

    @QtCore.Slot(str)
    @QtCore.Slot(str, str)
    @QtCore.Slot(str, str, bool)
    def appendRow(self, name, tex=None, show=False):
        self.names.add(name)
        self.tex[name] = tex
        if show:
            self.displayNames.add(name)
        self.isEmptyChanged.emit()


    @QtCore.Slot(object, object)
    def addParams(self, params, tex):
        self.beginResetModel()
        if list(self.names) == []: # Pandas Index can't be compared to a list
            self.names = params 
        else:
            self.names.intersection([params])
            self.tex = {}
        for name in self.names:
            try:
                self.tex[name] = tex[name]
            except KeyError:
                self.tex[name] = name
        if self.displayNames == {}:
            self.displayNames = set(self.names[:3])
        self.endResetModel()

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | \
               QtCore.Qt.ItemIsEnabled | \
               QtCore.Qt.ItemIsSelectable

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == ParameterModel.texRole:
            self.tex[self.names[index.row()]] = value
            self.dataChanged.emit(index, index)
            return True
        elif role == ParameterModel.selectedRole:
            show = value
            name = self.names[index.row()]
            if name in self.displayNames and show \
               or name not in self.displayNames and not show:
                return False
            else:
                if show:
                    self.displayNames.add(name)
                else:
                    self.displayNames.remove(name)
                self.dataChanged.emit(index, index)
                return True
        else:
            return False


class SamplesModel(QtCore.QAbstractListModel):
    # signals
    fullRepaint = QtCore.Signal(object, object)
    notify = QtCore.Signal(str)
    newParams = QtCore.Signal(object, object)
    minLogLChanged = QtCore.Signal()
    maxLogLChanged = QtCore.Signal()

    def _minLogL(self):
        try:
            return min(self.samples[x].logL.min() for x in self.samples) - 1
        except ValueError:
            return 0

    def _maxLogL(self):
        try: 
            return max(self.samples[x].logL.max() for x in self.samples)
        except ValueError:
            return 0

    isEmptyChanged = QtCore.Signal()

    def _isEmpty(self):
        return not self.hasChildren()

    isEmpty = QtCore.Property(bool, _isEmpty, notify=isEmptyChanged)
    
    minLogL = QtCore.Property(float, _minLogL, notify=minLogLChanged)
    maxLogL = QtCore.Property(float, _maxLogL, notify=maxLogLChanged)
    

    # Roles, i.e. properties for each model element
    nameRole = QtCore.Qt.UserRole + 1000 + 0
    urlRole = QtCore.Qt.UserRole + 1000 + 1
    legendNameRole = QtCore.Qt.UserRole + 1000 + 2
    displayRole = QtCore.Qt.UserRole + 1000 + 3
    legendColorRole = QtCore.Qt.UserRole + 1000 + 4
    samplesTypeRole = QtCore.Qt.UserRole + 1000 + 5
    legendAlphaRole = QtCore.Qt.UserRole + 1000 + 6
    logZRole = QtCore.Qt.UserRole + 1000 + 7
    dklRole = QtCore.Qt.UserRole + 1000 + 8
    bmdRole = QtCore.Qt.UserRole + 1000 + 9

    def roleNames(self):
        roles = {
            SamplesModel.nameRole: b'name',
            SamplesModel.urlRole: b'url',
            SamplesModel.legendNameRole: b'legend_name',
            SamplesModel.legendColorRole: b'legend_color',
            SamplesModel.samplesTypeRole: b'samples_type',
            SamplesModel.displayRole: b'display',
            SamplesModel.legendAlphaRole: b'legend_alpha',
            SamplesModel.logZRole: b'logZ',
            SamplesModel.dklRole: b'Dkl',
            SamplesModel.bmdRole: b'bmd',
        }
        return roles

    def count(self):
        return len(self.samples)
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        if len(self.names) != len(self.samples):
            raise ValueError(
                "len(samples) {} and len(samples_names) {}, mismatch."
                .format(len(self.names), len(self.samples)))
        return len(self.samples)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount() and index.isValid():
            item = self.samples[self.names[index.row()]]
            if role == SamplesModel.nameRole:
                return self.names[index.row()]
            if role == SamplesModel.urlRole:
                return item.root
            if role == SamplesModel.legendNameRole:
                return self.legends[self.names[index.row()]].title
            if role == SamplesModel.legendColorRole:
                return self.legends[self.names[index.row()]].color
            if role == SamplesModel.displayRole:
                return self.names[index.row()] in self.displayed_names
            if role == SamplesModel.samplesTypeRole:
                if isinstance(item, NestedSamples):
                    return 'NestedSamples'
                if isinstance(item, MCMCSamples):
                    return 'MCMCSamples'
            if role == SamplesModel.legendAlphaRole:
                return self.legends[self.names[index.row()]].alpha
            if role == SamplesModel.bmdRole:
                return float(self.samples[self.names[index.row()]].d())
            if role == SamplesModel.dklRole:
                return float(self.samples[self.names[index.row()]].D())
            if role == SamplesModel.logZRole:
                return float(self.samples[self.names[index.row()]].logZ())

    @QtCore.Slot(str)
    def appendRow(self, file_root, *args):
        rt, _ = cleanupFileRoot(file_root)
        if basename(rt) not in self.names:
            self.beginInsertRows(QtCore.QModelIndex(),
                                 self.rowCount(), self.rowCount())
            samples = NestedSamples(root=rt)
            if samples is None:
                raise ValueError('Samples were None')
            self.names.append(basename(rt))
            self.legends[basename(rt)] = Legend(basename(rt))
            self.samples[basename(rt)] = samples
            self.newParams.emit(samples.columns, samples.tex)
            self.displayed_names.add(basename(rt))
            self.endInsertRows()
            self.minLogLChanged.emit()
            self.maxLogLChanged.emit()
            self.requestRepaint()
            self.isEmptyChanged.emit()
        else:
            self.notify.emit(f'Samples: {basename(rt)} - already loaded.')

    def hasChildren(self):
        return len(self.samples)>0

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | \
               QtCore.Qt.ItemIsEnabled | \
               QtCore.Qt.ItemIsSelectable

    def requestRepaint(self):
        # TODO this should be broken down into specific kinds of adjustments
        # and individual signals that need to be handled. 
        samples = {k: self.samples[k] for k in self.displayed_names}
        legends = {k: self.legends[k] for k in self.displayed_names}
        self.fullRepaint.emit(samples, legends)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == SamplesModel.legendNameRole:
            self.legends[self.names[index.row()]].title = value
            self.dataChanged.emit(index, index)
            self.requestRepaint()
            return True
        if role == SamplesModel.legendColorRole:
            self.legends[self.names[index.row()]].color = value.name()
            self.legends[self.names[index.row()]].alpha = value.alphaF()
            self.dataChanged.emit(index, index)
            self.requestRepaint()
            return True
        if role == SamplesModel.legendAlphaRole:
            self.legends[self.names[index.row()]].alpha = value
            self.dataChanged.emit(index, index)
            self.requestRepaint()
            return True
        if role == SamplesModel.displayRole:
            name = self.names[index.row()]
            if name in self.displayed_names and value \
               or (name not in self.displayed_names) and not value:
                return False
            else:
                if value:
                    self.displayed_names.add(name)
                else:
                    self.displayed_names.remove(name)
                self.requestRepaint()
                return True
        else:
            return False

    

    def __init__(self, parent=None, names=[], samples={}):
        super().__init__(parent)
        self.names = names
        self.samples = samples
        self.legends = {}
        self.displayed_names = set()
        self.parameters = {}



