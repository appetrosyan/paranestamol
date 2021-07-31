"""The plotting and updating logic is hanlded in this file"""
from matplotlib.figure import Figure
from anesthetic import make_2d_axes
import numpy as np
from PySide2.QtCore import QUrl
from paranestamol import Legend, QtCore


def updateTrianglePlot(figure,
                       params,
                       tex,
                       samples,
                       legends,
                       logL,
                       kinds=None):
    figure, axes = make_2d_axes(params, tex=tex, fig=figure, upper=False)
    if kinds is None:
        kinds = {
            'lower': 'scatter',
            'diagonal': 'hist',
        }
    for x in samples:
        # FIXME: Strip off the weights
        samples[x]\
            .live_points(logL)\
            .plot_2d(axes,
                     alpha=legends[x].alpha,
                     color=legends[x].color,
                     label=legends[x].title,
                     types=kinds)
    handles, labels = axes[params[0]][params[1]]\
        .get_legend_handles_labels()
    figure.legend(handles, labels)
    # figure.tight_layout()
    # print(axes[params[0]][params[0]].patches)
    return figure


class TrianglePlotter(QtCore.QObject):
    """The class that handles the creation of the Plotting thread, the
plotting stack, and all changes of the GUI sliders."""
    notify = QtCore.Signal(str)
    paramsChanged = QtCore.Signal()
    reqNewTriangle = QtCore.Signal(object, object, object, object, object,
                                   float, object)
    lowerTypeChanged = QtCore.Signal()
    diagonalTypeChanged = QtCore.Signal()

    def __init__(self, paramsModel=None, parent=None):
        """Construct TrianglePlotter instance."""
        super().__init__(parent)
        self.logL = -1
        self.paramsModel = paramsModel
        self.legends = dict()
        self.samples = dict()
        self._LCache = dict()
        self._higson = HigsonPlotter()
        self._stack = ThreadedStackBuffer()
        self._thread = QtCore.QThread(parent=self)
        self._thread.start()
        self._worker = ThreadedPlotter()
        self._worker.moveToThread(self._thread)
        self.reqNewTriangle.connect(self._stack.push)
        self._stack.popped.connect(self._worker.plot_triangle)
        self._worker.finished.connect(self.cacheTriangleFigure)
        self._invalidating = False
        self.plotTypes = {
            'lower': 'scatter',
            'diagonal': 'hist',
        }

    def get_lowerType(self):
        """Get lower plot type."""
        return self.plotTypes['lower']

    def set_lowerType(self, other):
        """Set lower plot type."""
        if other in {"kde", "scatter", "fastkde"}:
            self.plotTypes['lower'] = other
            self.reDraw()
        else:
            raise ValueError(f'{other} lower plot type is not recognised. ')

    lowerType = QtCore.Property(str,
                                fget=get_lowerType,
                                fset=set_lowerType,
                                notify=lowerTypeChanged)

    def get_diagonalType(self):
        """Get diagonal plot type."""
        return self.plotTypes['diagonal']

    def set_diagonalType(self, other):
        """Set diagonal plot type."""
        if other in {'kde', 'hist'}:
            self.plotTypes['diagonal'] = other
            self.reDraw()
        else:
            raise ValueError(f'{other} diagonal plot type is not recognised. ')

    diagonalType = QtCore.Property(str,
                                   fget=get_diagonalType,
                                   fset=set_diagonalType,
                                   notify=diagonalTypeChanged)

    @property
    def beta(self):
        """Nested sampling temperature."""
        return self._higson.beta

    @beta.setter
    def beta(self, other: float):
        """Setter for nested sampling temperature."""
        self._higson.beta = other

    @property
    def higCanvas(self):
        """Get the canvas to plot a Higson plot to."""
        return self._higson.higCanvas()

    @higCanvas.setter
    def higCanvas(self, other):
        """Set the canvas to plot the Higson plot to."""
        self._higson.higCanvas = other

    @property
    def params(self):
        """Get all of the parameters available."""
        return list(self.paramsModel.displayNames)

    @property
    def tex(self):
        """Get the parameters' LaTeX representation."""
        return self.paramsModel.tex

    @QtCore.Slot(float, object)
    def cacheTriangleFigure(self, logL, fig):
        """Cache a triangle figure."""
        self._stack.pop()
        if not self._invalidating:
            self._LCache[logL] = fig
            if self.logL == logL:
                self._updateTriangleFigure(self._LCache[logL])
                self.notify.emit("Finished!")
        else:
            while self._worker.busy:
                pass
            self._invalidating = False
            self.notify.emit('Cache cleared!')

    @QtCore.Slot(object)
    def _updateTriangleFigure(self, fig):
        self.triCanvas.figure = fig
        fig.set_canvas(self.triCanvas)
        self.triCanvas.draw_idle()

    def request_update_triangle(self, post=None, logL: float = -1):
        """Enqueue update of the triangle figure into a threaded plotter."""
        fig = self.triCanvas.figure
        figsize = fig.get_figwidth(), fig.get_figheight()
        self.reqNewTriangle.emit(Figure(figsize=figsize), self.params,
                                 self.tex, self.samples, self.legends, logL,
                                 self.plotTypes)

    @QtCore.Slot(str)
    def saveFigure(self, filename: str):
        """Save the current Triangle Plot to a file."""
        url = QUrl(filename)
        if filename.endswith(".gif"):
            self.notify.emit("requested a GIF. Not yet supported")
        self.triCanvas.figure.savefig(fname=url.toLocalFile())

    @QtCore.Slot()
    @QtCore.Slot(object, object)
    def invalidateCache(self, *args):
        """Invalidate the cache and start plotting all over."""
        self.notify.emit("re-building cache. Please wait.")
        self._invalidating = True
        self._stack.clear_buffer()
        old_cache = self._LCache.keys()
        self._LCache = {}
        for x in old_cache:
            self.request_update_triangle(logL=x)
        self._stack.pop()

    @QtCore.Slot(float)
    def changeLogL(self, logL, *args):
        """Request change of logL and re-plot."""
        self.logL = logL
        if self.logL in self._LCache:
            wh = self.triCanvas.figure.get_size_inches()
            self.triCanvas.figure = self._LCache[self.logL]
            self._LCache[self.logL].set_canvas(self.triCanvas)
            self.triCanvas.figure.set_size_inches(wh)
            self.triCanvas.draw_idle()
        else:
            self.request_update_triangle(logL=self.logL)

    @QtCore.Slot(float)
    def changeTemperature(self, beta, *args):
        """Change the nested samples' temperature and request an update to the affected plot."""
        self.beta = beta
        self._higson._update_higson(self.samples, self.legends)

    @QtCore.Slot()
    @QtCore.Slot(object)
    @QtCore.Slot(object, object)
    def reDraw(self, samples=None, legends=None, *args):
        """Request a complete redraw."""
        if not isinstance(samples, QtCore.QModelIndex) and not isinstance(
                legends, QtCore.QModelIndex):
            if samples is not None:
                self.samples = samples
            if legends is None and self.legends is None:
                for k in self.samples:
                    self.legends[k] = Legend(title=k)
            elif legends is not None:
                self.legends = legends
        self.invalidateCache()
        self._stack.pop()
        self._higson._update_higson(self.samples, self.legends)


class HigsonPlotter(QtCore.QObject):
    """A class that handles the plotting and deployment of a higson plot."""
    def __init__(self, parent=None):
        """Construct a higson Plotter."""
        super().__init__(parent)
        self._beta = 1
        self._cache = {}

    @property
    def beta(self):
        """Nested Samples' temperature."""
        return self._beta

    @beta.setter
    def beta(self, other):
        self._beta = other

    @property
    def higCanvas(self):
        """Higson canvas to plot to."""
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
                    logX = np.log(samples[x].nlive /
                                  (samples[x].nlive + 1)).cumsum()
                LXi = samples[x].logL / self.beta + logX
                LX = np.exp(LXi - LXi.max())
                try:
                    self._cache[self.beta][x] = (logX, LX)
                except KeyError:
                    self._cache[self.beta] = {}
                    self._cache[self.beta][x] = (logX, LX)
            self.ax.plot(logX[::-1], LX, color=legends[x].color)
        self.higCanvas.draw_idle()


class ThreadedPlotter(QtCore.QObject):
    """A Qt Threading based signal operated plotter."""
    finished = QtCore.Signal(float, object)

    @QtCore.Slot(object, object, object, object, object, float)
    @QtCore.Slot(object, object, object, object, object, float, object)
    def plot_triangle(self, *args):
        """Start plotting a triangle plot"""
        self.busy = True
        fig = updateTrianglePlot(*args)
        self.finished.emit(args[-2], fig)
        self.busy = False


class ThreadedStackBuffer(QtCore.QObject):
    """A threaded stack buffer used to handle the plotting stack."""

    popped = QtCore.Signal(object, object, object, object, object, float,
                           object)

    def __init__(self, parent=None):
        """Create a ThreadedStackBuffer instance."""
        super().__init__(parent)
        self._buffer = []
        self.autopop = True

    def clear_buffer(self):
        """Clear the plotting buffer."""
        self._buffer = []

    def pop(self):
        """Pop the stack buffer."""
        try:
            self.autopop = False
            self.popped.emit(*self._buffer.pop())
        except:  # TODO: figure out what kind of exception is thrown.
            self.autopop = True

    @QtCore.Slot(object, object, object, object, object, float, object)
    def push(self, *args):
        """Push an object to the stack buffer."""
        self._buffer.append(args)
        if self.autopop:
            self.pop()
