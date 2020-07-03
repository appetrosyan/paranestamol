"""This module defines the abstracListModel subclass that is used to
keep the QML model in sync with the Python back end.

"""
from matplotlib_backend_qtquick.qt_compat import QtCore
from anesthetic.samples import NestedSamples, MCMCSamples
from os.path import splitext, basename
import matplotlib.pyplot as plt


class Legend:
    colorCycles = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    currentColor = 0

    def __init__(self, title='', color=None, alpha=None):
        self.title = title
        if color is not None:
            self.color = color  # Let's be international.
        else:
            self.color = Legend.colorCycles[Legend.currentColor
                                            % len(Legend.colorCycles)]
        if alpha is None:
            self.alpha = 1
        Legend.currentColor += 1

        @property
        def color(self):
            return self._color

        @color.setter
        def color_(self, color):
            if isinstance(color, str):
                if len(color > 7):
                    self._color = '#{}'.format(color[3:])
                    self.alpha = int(color[1:3], 16)/int("ff", 16)


class ParameterModel(QtCore.QAbstractListModel):
    nameRole = QtCore.Qt.UserRole + 1000 + 0
    texRole = QtCore.Qt.UserRole + 1000 + 1
    selectedRole = QtCore.Qt.UserRole + 1000 + 2

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

    @QtCore.Slot(object, object)
    def addParams(self, params, tex):
        self.beginResetModel()
        if self.names == []:
            self.names = params
        else:
            self.names.intersection([params])
            self.tex = {}
        for name in self.names:
            self.tex[name] = tex[name]
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
            name = self.names[index.row()]
            if name in self.displayNames and value \
               or name not in self.displayNames and not value:
                return False
            else:
                if value:
                    self.displayNames.add(name)
                else:
                    self.displayNames.remove(name)
                self.dataChanged.emit(index, index)
                return True
        else:
            return False


class SamplesModel(QtCore.QAbstractListModel):
    fullRepaint = QtCore.Signal(object, object)
    notify = QtCore.Signal(str)
    newParams = QtCore.Signal(object, object)

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
        self.notify.emit('Loading...')
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

            self.reqRepaint()
            self.notify.emit('Loaded.')
        else:
            self.notify.emit(f'Samples: {basename(rt)} - already loaded.')

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | \
               QtCore.Qt.ItemIsEnabled | \
               QtCore.Qt.ItemIsSelectable

    def reqRepaint(self):
        samples = {k: self.samples[k] for k in self.displayed_names}
        legends = {k: self.legends[k] for k in self.displayed_names}
        self.fullRepaint.emit(samples, legends)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == SamplesModel.legendNameRole:
            self.legends[self.names[index.row()]].title = value
            self.dataChanged.emit(index, index)
            self.reqRepaint()
            return True
        if role == SamplesModel.legendColorRole:
            self.legends[self.names[index.row()]].color = value.name()
            self.legends[self.names[index.row()]].alpha = value.alphaF()
            self.dataChanged.emit(index, index)
            self.reqRepaint()
            return True
        if role == SamplesModel.legendAlphaRole:
            self.legends[self.names[index.row()]].alpha = value
            self.dataChanged.emit(index, index)
            self.reqRepaint()
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
                self.reqRepaint()
                return True
        else:
            return False

    def __init__(self, parent=None, names=[], samples={}):
        super(SamplesModel, self).__init__(parent)
        self.names = names
        self.samples = samples
        self.legends = {}
        self.displayed_names = set()
        self.parameters = {}


def cleanupFileRoot(file_root):
    ret = file_root.replace('file://', '', 1)
    exts = ['.stats', '.resume', '.paramnames', '.inputparams', '.ranges']
    # Make sure to put the substrings later, so that the longer part can be picked up.
    ends = ['_equal_weights', '_dead-birth', '_dead','_phys_live-birth',  '_phys_live']
    root, ext = splitext(ret)
    if ext in exts:
        return root, ext
    elif ext == '.txt':
        for end in ends:
            try:
                rt, end = root.rsplit(end, 1)
                return rt, end+ext
            except ValueError:
                pass
