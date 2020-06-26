from matplotlib_backend_qtquick.qt_compat import QtCore
import matplotlib.pyplot as plt
from multiprocessing import Pool
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
        self.worker = ScreenPainter(self)

    @property
    def params(self):
        return list(self.paramsModel.displayNames)

    @property
    def tex(self):
        return self.paramsModel.tex

    @QtCore.Slot(float)
    def changeLogL(self, logL, *args):
        self.logL = logL
        self._update()

    @QtCore.Slot(float)
    def changeTemperature(self, beta, *args):
        self.beta = beta
        self._update()

    def _update(self):
        self.notify.emit('repainting')
        w, h = self.canvas.figure.get_figwidth(), self.canvas.figure.get_figheight()
        self.worker.figure = plt.figure(figsize=(w, h))
        self.worker.params = self.params
        self.worker.tex = self.tex
        self.worker.samples = self.samples
        self.worker.legends = self.legends
        self.worker.logL = self.logL
        self.worker.beta = self.beta

        self.worker.done.connect(self.paintFigure)
        self.worker.start()

    @QtCore.Slot(object)
    def paintFigure(self, fig):
        self.canvas.figure = fig
        fig.set_canvas(self.canvas)
        self.canvas.draw_idle()
        self.notify.emit('View Updated.')

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
        self._update()


def updateTrianglePlot(figure, params, tex, samples, legends,
                       logL=None, beta=None):
    figure, axes = make_2d_axes(params, tex=tex, fig=figure)
    for x in samples:
        samples[x].plot_2d(axes,
                           alpha=legends[x].alpha,
                           color=legends[x].color,
                           label=legends[x].title)

    handles, labels = axes[params[0]][params[1]]\
        .get_legend_handles_labels()
    figure.legend(handles, labels)
    return figure


class ScreenPainter(QtCore.QThread):
    done = QtCore.Signal(object)

    def __init__(self, parent, figure=None, params=None, tex=None, samples=None,
                 legends=None, logL=None, beta=None):
        QtCore.QThread.__init__(self, parent)
        self.figure = figure
        self.params = params
        self.tex = tex
        self.samples = samples
        self.legends = legends
        self.logL = logL
        self.beta = beta

    def run(self):
        args = (self.figure, self.params, self.tex,
                self.samples, self.legends, self.logL,
                self.beta)
        # with Pool(1) as p:
            # fig = p.starmap(updateTrianglePlot, [args])
        # fig = fig[0]
        fig = updateTrianglePlot(*args)
        self.done.emit(fig)
        self.quit()
