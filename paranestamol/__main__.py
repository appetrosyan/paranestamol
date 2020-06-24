#!/usr/bin/env python
"""
An example of using the backend
"""
import sys
from pathlib import Path
from matplotlib_backend_qtquick.backend_qtquickagg import FigureCanvasQtQuickAgg
from matplotlib_backend_qtquick.qt_compat import QtGui, QtQml, QtCore
from anesthetic.plot import make_2d_axes
from .samples_model import SamplesModel
import matplotlib.pyplot as plt




class DisplayBridge(QtCore.QObject):
    notify = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = None
        self._coordinates = ""
        self.beta = 0
        self.canvas = None
        # self.axes = None
        self._sample = None
        self.samples = dict()
        self.params = []

   


    @QtCore.Slot(int)
    def changeTemperature(self, beta, *args):
        self.beta = beta
        fig = updateTrianglePlot(self, plt.figure())
        self.canvas.figure = fig
        fig.set_canvas(self.canvas)
        self.canvas.draw_idle()

    @QtCore.Slot(object, object)
    def reDraw(self, samples=None, legends=None, *args):
        if samples:
            self.samples = samples
        if legends:
            self.legends = legends
        if self.params == []:
            q, r = self.samples.popitem()
            # Proof python was designed by morons!
            self.samples[q] = r
            # end proof
            self.params = [y for y in self.samples[q].columns[:3]]
        updateTrianglePlot(self, self.canvas.figure)
        self.canvas.draw_idle()


def updateTrianglePlot(bridge, figure):
    figure.clear()
    figure, axes = make_2d_axes(bridge.params, fig=figure)
    for x in bridge.samples:
        bridge.samples[x].plot_2d(axes, alpha=0.7,
                                  color=bridge.legends[x].color,
                                  label=bridge.legends[x].title)
    handles, labels = axes[bridge.params[0]][bridge.params[1]]\
        .get_legend_handles_labels()
    figure.legend(handles, labels)
    return figure


def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    sys.argv += ['--style', 'material']
    app = QtGui.QGuiApplication(sys.argv)
    engine = QtQml.QQmlApplicationEngine()
    displayBridge = DisplayBridge()

    context = engine.rootContext()
    context.setContextProperty("displayBridge", displayBridge)
    samplesModel = SamplesModel()
    samplesModel.repaint.connect(displayBridge.reDraw)
    context.setContextProperty("samplesModel", samplesModel)
    QtQml.qmlRegisterType(FigureCanvasQtQuickAgg,
                          "Backend", 1, 0, "FigureCanvas")
    qmlFile = Path(Path.cwd(), Path(__file__).parent, "view.qml")
    engine.load(QtCore.QUrl.fromLocalFile(str(qmlFile)))
    win = engine.rootObjects()[0]
    displayBridge.notify.connect(win.displayPythonMessage)
    # samplesModel.notify.connect(win.displayPythonMessage)

    displayBridge.canvas = win.findChild(QtCore.QObject, "trianglePlot")
    displayBridge.figure = displayBridge.canvas.figure
    app.exec_()


if __name__ == "__main__":
    main()
