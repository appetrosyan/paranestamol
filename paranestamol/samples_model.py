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


class ParameterModel(QtCore.QAbstractListModel):
    nameRole = QtCore.Qt.UserRole + 1000 + 0
    texRole = QtCore.Qt.UserRole + 1000 + 1
    selectedRole = QtCore.Qt.UserRole + 1000 + 2

    def __init__(self, parent=None, sample=None):
        super(ParameterModel, self).__init__(parent)
        self.names = sample.columns
        print('created')
        self.displayNames = set(sample.columns[:3])

    def roleNames(self):
        roles = {
            ParameterModel.nameRole: b'name',
            ParameterModel.texRole: b'tex',
            ParameterModel.selectedRole: b'selected'
        }
        return roles

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.params)

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


class SamplesModel(QtCore.QAbstractListModel):
    fullRepaint = QtCore.Signal(object, object, object)
    notify = QtCore.Signal(str)

    nameRole = QtCore.Qt.UserRole + 1000 + 0
    urlRole = QtCore.Qt.UserRole + 1000 + 1
    legendNameRole = QtCore.Qt.UserRole + 1000 + 2
    displayRole = QtCore.Qt.UserRole + 1000 + 3
    legendColorRole = QtCore.Qt.UserRole + 1000 + 4
    samplesTypeRole = QtCore.Qt.UserRole + 1000 + 5
    parametersModel = QtCore.Qt.UserRole + 1000 + 6

    def roleNames(self):
        roles = {
            SamplesModel.nameRole: b'name',
            SamplesModel.urlRole: b'url',
            SamplesModel.legendNameRole: b'legend_name',
            SamplesModel.legendColorRole: b'legend_color',
            SamplesModel.samplesTypeRole: b'samples_type',
            SamplesModel.displayRole: b'display',
            SamplesModel.parametersModel: b'parameters_model'
        }
        return roles

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        if len(self.names) != len(self.samples):
            raise ValueError(
                f"Number of samples {len(self.names)} must match number of samples_names {len(self.samples)}.")
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
            if role == SamplesModel.parametersModel:
                return self.parameters[self.names[index.row()]]

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
            self.parameters[basename(rt)] = ParameterModel(self, self.samples[basename(rt)])
            print(self.parameters)
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
        a, b = self.parameters.popitem()
        displayed_params = b.displayNames
        for k in self.parameters:
            displayed_params = displayed_params.intersection(self.parameters[k].displayNames)
        # This isn't the first time. You'll see this stupid pattern again.
        self.parameters[a] = b

        self.fullRepaint.emit({k: self.samples[k] for k in self.displayed_names},
                              {k: self.legends[k] for k in self.displayed_names},
                              list(displayed_params))

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
        self.names = []
        self.samples = {}
        self.legends = {}
        self.displayed_names = set()
        self.parameters = {}


def cleanupFileRoot(file_root):
    ret =file_root.replace('file://', '', 1)
    exts = ['.stats', '.resume', '.paramnames', '.inputparams', '.ranges']
    # Make sure to put the substrings later, so that the longer part can be picked up.
    ends = ['_equal_weights', '_dead-birth', '_dead','_phys_live-birth',  '_phys_live']
    root, ext = splitext(ret)
    print(f'{root}, {ext}')
    if ext in exts:
        return root, ext
    elif ext == '.txt':
        for end in ends:
            try:
                rt, end = root.rsplit(end, 1)
                return rt, end+ext
            except ValueError:
                pass 
