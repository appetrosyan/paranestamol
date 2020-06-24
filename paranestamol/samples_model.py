"""This module defines the abstracListModel subclass that is used to
keep the QML model in sync with the Python back end.

"""

from matplotlib_backend_qtquick.qt_compat import QtCore
from anesthetic.samples import NestedSamples, MCMCSamples
from os.path import splitext, basename


class Legend:
    def __init__(self, title='', color='#ff0000'):
        self.title = title
        self.color = color  # Let's be international.


class SamplesModel(QtCore.QAbstractListModel):
    fullRepaint = QtCore.Signal(object, object)
    notify = QtCore.Signal(str)

    nameRole = QtCore.Qt.UserRole + 1000 + 0
    urlRole = QtCore.Qt.UserRole + 1000 + 1
    legendNameRole = QtCore.Qt.UserRole + 1000 + 2
    displayRole = QtCore.Qt.UserRole + 1000 + 3
    legendColorRole = QtCore.Qt.UserRole + 1000 + 4
    samplesTypeRole = QtCore.Qt.UserRole + 1000 + 5

    def roleNames(self):
        roles = {
            SamplesModel.nameRole: b'name',
            SamplesModel.urlRole: b'url',
            SamplesModel.legendNameRole: b'legend_name',
            SamplesModel.legendColorRole: b'legend_color',
            SamplesModel.samplesTypeRole: b'samples_type',
            SamplesModel.displayRole: b'display',
        }
        return roles

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        if len(self.names) != len(self.samples):
            raise ValueError(
                f"Number of samples must match number of samples_names. {len(self.names)}, {len(self.samples)}")
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

    @QtCore.Slot(str)
    def appendRow(self, file_root, *args):
        rt, _ = splitext(file_root)
        self.notify.emit('Loading...')
        if basename(rt) not in self.names:
            self.beginInsertRows(QtCore.QModelIndex(),
                                 self.rowCount(), self.rowCount())
            samples = NestedSamples(root=rt)
            if samples is not None:
                self.names.append(basename(rt))
                self.legends[basename(rt)] = Legend(basename(rt))
                self.samples[basename(rt)] = samples
                self.displayed_names.add(basename(rt))
            self.endInsertRows()
            self.reqRepaint()
            self.notify.emit('Loaded.')
        else:
            self.notify.emit(f'Samples named: {basename(rt)} - already loaded.')
            raise KeyError(
                f'samples named \'{basename(rt)}\' already present.')

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | \
               QtCore.Qt.ItemIsEnabled | \
               QtCore.Qt.ItemIsSelectable

    def reqRepaint(self):
        self.fullRepaint.emit({k: self.samples[k] for k in self.displayed_names},
                              {k: self.legends[k] for k in self.displayed_names})

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == SamplesModel.legendNameRole:
            self.legends[self.names[index.row()]].title = value
            self.dataChanged.emit(index, index)
            self.reqRepaint()
            return True
        if role == SamplesModel.legendColorRole:
            self.legends[self.names[index.row()]].color = value.name()
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
        return False

    def __init__(self, parent=None):
        super(SamplesModel, self).__init__(parent)
        self.notify.emit('Python is degisned by morons. Pyside2 is very pythonic indeed. ')
        self.names = []
        self.samples = {}
        self.legends = {}
        self.displayed_names = set()
