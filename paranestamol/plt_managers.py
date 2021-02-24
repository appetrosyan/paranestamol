from matplotlib_backend_qtquick.qt_compat import QtCore
from matplotlib.figure import Figure
from anesthetic import make_2d_axes
# import pathos.pools as pp
from .samples_model import Legend
import numpy as np
from multiprocessing import Pool


def updateTrianglePlot(figure, params, tex, samples, legends, logL):
    figure, axes = make_2d_axes(params, tex=tex, fig=figure, upper=False)
    for x in samples:
        samples[x]\
            .live_points(logL)\
            .plot_2d(axes,
                     alpha=legends[x].alpha,
                     color=legends[x].color,
                     label=legends[x].title,
                     types={
                         'lower': 'scatter',
                         'diagonal': 'hist',
                     })
    handles, labels = axes[params[0]][params[1]]\
        .get_legend_handles_labels()
    figure.legend(handles, labels)
    return figure


class TrianglePlotter(QtCore.QObject):
    notify = QtCore.Signal(str)
    paramsChanged = QtCore.Signal()
    reqNewTriangle = QtCore.Signal(object, object, object, object, object, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logL = -1
        self.triCanvas = None
        self.legends = {}
        self.samples = dict()
        self.paramsModel = None
        self._LCache = {}
        self._higson = HigsonPlotter()
        self._stack = ThreadedStackBuffer()
        self._thread = QtCore.QThread(parent=self)
        self._thread.start()
        self._worker = ThreadedPlotter()
        self._worker.moveToThread(self._thread)
        self.reqNewTriangle.connect(self._stack.push)
        self._stack.popped.connect(self._worker.plot_triangle)
        self._worker.finished.connect(self.cacheTriangleFigure)


    @property
    def beta(self):
        return self._higson.beta

    @beta.setter
    def beta(self, other):
        self._higson.beta = other


    @property
    def higCanvas(self):
        return self._higson.higCanvas()

    @higCanvas.setter
    def higCanvas(self, other):
        self._higson.higCanvas = other

    @property
    def params(self):
        return list(self.paramsModel.displayNames)

    @property
    def tex(self):
        return self.paramsModel.tex

    @QtCore.Slot(float, object)
    def cacheTriangleFigure(self, logL, fig):
        self._stack.pop()
        self._LCache[logL] = fig
        if self.logL == logL:
            self._updateTriangleFigure(self._LCache[logL])


    @QtCore.Slot(object)
    def _updateTriangleFigure(self, fig):
        self.triCanvas.figure = fig
        fig.set_canvas(self.triCanvas)
        self.triCanvas.draw_idle()

    def request_update_triangle(self, post=None, logL=-1):
        fig = self.triCanvas.figure
        figsize = fig.get_figwidth(), fig.get_figheight()
        self.reqNewTriangle.emit(Figure(figsize=figsize),
                                 self.params, self.tex,
                                 self.samples, self.legends, logL)

    @QtCore.Slot()
    @QtCore.Slot(object, object)
    def invalidateCache(self, *args):
        self._stack.clear_buffer()
        old_cache = self._LCache
        self._LCache = {}
        for x in old_cache:
            self.request_update_triangle(logL=x)
        self._stack.pop()

    @QtCore.Slot(float)
    def changeLogL(self, logL, *args):
        self.logL = logL
        if self.logL in self._LCache:
            self.triCanvas.figure = self._LCache[self.logL]
            self._LCache[self.logL].set_canvas(self.triCanvas)
            self.triCanvas.draw_idle()
        else:
            self.request_update_triangle(logL= self.logL)

    @QtCore.Slot(float)
    def changeTemperature(self, beta, *args):
        self.beta = beta
        self._higson._update_higson(self.samples, self.legends)

    @QtCore.Slot()
    @QtCore.Slot(object)
    @QtCore.Slot(object, object)
    def reDraw(self, samples=None, legends=None, *args):
        if samples is not None and not isinstance(samples, QtCore.QModelIndex):
            self.samples = samples
        if legends is None and self.legends is None:
                for k in self.samples:
                    self.legends[k] = Legend(title=k)
        else:
            # Fuck the Duck typing.
            if not isinstance(legends, QtCore.QModelIndex):
                self.legends = legends
        self._stack.pop()
        self._higson._update_higson(self.samples, self.legends)


class HigsonPlotter(QtCore.QObject):
    def __init__(self,  parent=None):
        super().__init__(parent)
        self._beta = 1
        self._cache = {}

    @property
    def beta(self):
        return self._beta

    @beta.setter
    def beta(self, other):
        self._beta = other

    @property
    def higCanvas(self):
        return self._higCanvas

    @higCanvas.setter
    def higCanvas(self, other):
        self._higCanvas = other
        self.ax = self.higCanvas.figure.gca()
        self.ax.cla()
        self.ax.xaxis.set_tick_params(labeltop='on')
        self.ax.xaxis.set_tick_params(labelbottom=False)
        self.ax.set_xlabel(r'$\log X$')
        self.ax.set_ylabel(r'$LX$', labelpad=-30)
        self.higCanvas.figure.set_tight_layout({'pad': 0})

    def _update_higson(self, samples, legends):
        self.ax.lines.clear()
        for x in samples:
            if self.beta in self._cache and x in self._cache[self.beta]:
                logX, LX = self._cache[self.beta][x]
            else:
                with np.errstate(divide='ignore'):
                    logX = np.log(samples[x].nlive / (samples[x].nlive+1)).cumsum()
                LXi = samples[x].logL/self.beta + logX
                LX = np.exp(LXi-LXi.max())
                try:
                    self._cache[self.beta][x] = (logX, LX)
                except KeyError as e:
                    self._cache[self.beta] = {}
                    self._cache[self.beta][x] = (logX, LX)
            self.ax.plot(logX[::-1], LX, color=legends[x].color)
        self.higCanvas.draw_idle()

class ThreadedPlotter(QtCore.QObject):
    finished = QtCore.Signal(float, object)

    @QtCore.Slot(object, object, object, object, object, float)
    def plot_triangle(self, *args):
        self.busy=True
        fig = updateTrianglePlot(*args)
        self.finished.emit(args[-1], fig)
        self.busy=False


class ThreadedStackBuffer(QtCore.QObject):
    popped = QtCore.Signal(object, object, object, object, object, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._buffer = []
        self.autopop = True

    def clear_buffer(self):
        self._buffer = []

    def pop(self):
        try:
            self.autopop=False
            self.popped.emit(*self._buffer.pop())
        except:
            self.autopop=True


    @QtCore.Slot(object, object, object, object, object, float)
    def push(self, *args):
        self._buffer.append(args)
        if self.autopop:
            self.pop()
