from matplotlib_backend_qtquick.qt_compat import QtCore
import matplotlib.pyplot as plt
from anesthetic import make_2d_axes
import numpy as np
from .samples_model import ParameterModel



class TrianglePlotter(QtCore.QObject):
    notify = QtCore.Signal(str)
    paramsChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = None
        self._coordinates = ""
        self.beta = 0
        self.logL = -10000
        self.canvas = None
        # self.axes = None
        self._sample = None
        self.samples = dict()
        self.params = []
        self._paramsModel = None

    @QtCore.Slot(object, object)
    def updateParams(self, columns, tex):
        print('updating params')
        self._paramsModel = ParameterModel(self, columns, tex)
        self.params = list(self._paramsModel.displayNames)
        self.paramsChanged.emit()

    @QtCore.Slot(float)
    def changeLogL(self, logL, *args):
        self.logL = logL
        print(logL)
        fig = updateTrianglePlot(self, plt.figure(), logL = 10*logL)
        self.canvas.figure = fig
        fig.set_canvas(self.canvas)
        self.canvas.draw_idle()

    @QtCore.Slot(float)
    def changeTemperature(self, beta, *args):
        self.beta = beta
        for k in self.samples:
            self.samples.beta = beta
        fig = updateTrianglePlot(self, plt.figure())
        self.canvas.figure = fig
        fig.set_canvas(self.canvas)
        self.canvas.draw_idle()

    @QtCore.Slot(object, object)
    @QtCore.Slot(object, object, object)
    def reDraw(self, samples=None, legends=None, params=None, *args):
        print('repainting')
        if samples:
            self.samples = samples
        if legends:
            self.legends = legends
        if params is not None:
            self.params = params
        print(self.params)
        self.notify.emit('Full repaint...')
        updateTrianglePlot(self, self.canvas.figure)
        self.notify.emit('Fully repainted.')
        self.canvas.draw_idle()


def updateTrianglePlot(bridge, figure, logL=None):
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
