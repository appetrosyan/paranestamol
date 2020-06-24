from matplotlib_backend_qtquick.qt_compat import QtCore
import matplotlib.pyplot as plt
from anesthetic import make_2d_axes
import numpy as np



class TrianglePlotter(QtCore.QObject):
    notify = QtCore.Signal(str)

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
        print(beta)
        fig = updateTrianglePlot(self, plt.figure())
        self.canvas.figure = fig
        fig.set_canvas(self.canvas)
        self.canvas.draw_idle()

    @QtCore.Slot(object, object)
    def reDraw(self, samples=None, legends=None, *args):
        print('repainting')
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
