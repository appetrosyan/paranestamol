#!/usr/bin/env python
"""
An example of using the backend
"""
import sys
from pathlib import Path
from os.path import splitext, relpath
from matplotlib_backend_qtquick.backend_qtquickagg import FigureCanvasQtQuickAgg
from matplotlib_backend_qtquick.qt_compat import QtGui, QtQml, QtCore
from anesthetic.plot import make_2d_axes

class DisplayBridge(QtCore.QObject):
    coordinatesChanged = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = None
        self._coordinates = ""
        self.offset = 0
        self.canvas = None
        self.axes = None
        self._samples = None
        self.samples = dict()

    def updateWithCanvas(self, canvas=None):
        if canvas is not None:
            self.canvas = canvas
            self.figure = canvas.figure
        if self.samples:
            self.figure.clear()
            for x in self.samples:
                params = [y for y in self.samples[x].columns[:5]]
                self.figure, self.axes = make_2d_axes(params)
            self.canvas.draw_idle()

    @QtCore.Slot(int)
    def changeTemperature(self, x, *args):
        """Modify the temperature."""
        self.offset = x
        self.updateWithCanvas(self.canvas)

    @QtCore.Slot(str, result=str)
    def loadSamples(self, file_root, *args):
        try:
            from anesthetic import NestedSamples
            rt, _ = splitext(file_root)
            self._samples = NestedSamples(root=rt)
            return str(relpath(rt))
        except ImportError:
            print("Cannot import anesthetic.")

    @QtCore.Slot(str)
    def loadSamplesCallback(self, name, *args):
        self.samples[name] = self._samples
        print(name)


def main():
    """Main function."""
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    sys.argv += ['--style', 'material']
    app = QtGui.QGuiApplication(sys.argv)
    engine = QtQml.QQmlApplicationEngine()
    displayBridge = DisplayBridge()
    context = engine.rootContext()
    context.setContextProperty("displayBridge", displayBridge)
    QtQml.qmlRegisterType(FigureCanvasQtQuickAgg,
                          "Backend", 1, 0, "FigureCanvas")
    qmlFile = Path(Path.cwd(), Path(__file__).parent, "view.qml")
    engine.load(QtCore.QUrl.fromLocalFile(str(qmlFile)))
    win = engine.rootObjects()[0]
    displayBridge.updateWithCanvas(win.findChild(QtCore.QObject, "figure"))
    app.exec_()


if __name__ == "__main__":
    main()
