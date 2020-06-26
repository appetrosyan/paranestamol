from matplotlib_backend_qtquick.qt_compat import QtCore
import matplotlib.pyplot as plt
from anesthetic import make_2d_axes
from .samples_model import Legend


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
        self._sample = None
        self.legends = {}
        self.samples = dict()
        self.paramsModel = None

    @property
    def params(self):
        return list(self.paramsModel.displayNames)

    @property
    def tex(self):
        return self.paramsModel.tex

    @QtCore.Slot(float)
    def changeLogL(self, logL, *args):
        self.logL = logL
        fig = updateTrianglePlot(self, plt.figure())
        self.canvas.figure = fig
        fig.set_canvas(self.canvas)
        self.canvas.draw_idle()

    @QtCore.Slot(float)
    def changeTemperature(self, beta, *args):
        self.beta = beta
        fig = updateTrianglePlot(self, plt.figure())
        self.canvas.figure = fig
        fig.set_canvas(self.canvas)
        self.canvas.draw_idle()

    @QtCore.Slot()
    @QtCore.Slot(object)
    @QtCore.Slot(object, object)
    def reDraw(self, samples=None, legends=None, *args):
        if samples:
            self.samples = samples
        if legends is None:
            if self.legends is None:
                for k in self.samples:
                    self.legends[k] = Legend(title=k)
        else:
            self.legends = legends
        self.notify.emit('Full repaint...')
        updateTrianglePlot(self, self.canvas.figure)
        self.notify.emit('Fully repainted.')
        self.canvas.draw_idle()


def updateTrianglePlot(bridge, figure, logL=None):
    figure.clear()
    print(bridge.params)
    figure, axes = make_2d_axes(bridge.params, tex=bridge.tex, fig=figure)
    for x in bridge.samples:
        bridge.samples[x].live_points(bridge.logL)\
                         .plot_2d(axes,
                                  alpha=bridge.legends[x].alpha,
                                  color=bridge.legends[x].color,
                                  label=bridge.legends[x].title)
    handles, labels = axes[bridge.params[0]][bridge.params[1]]\
        .get_legend_handles_labels()
    figure.legend(handles, labels)
    return figure