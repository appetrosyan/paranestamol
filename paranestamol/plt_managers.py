from matplotlib_backend_qtquick.qt_compat import QtCore
import matplotlib.pyplot as plt
from anesthetic import make_2d_axes
from .samples_model import Legend
import numpy as np



class TrianglePlotter(QtCore.QObject):
    notify = QtCore.Signal(str)
    paramsChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.beta = 1
        self.logL = -10000
        self.triCanvas = None
        self.higCanvas = None
        self._sample = None
        self.legends = {}
        self.samples = dict()
        self.paramsModel = None
        self._betaCache = {}
        self._LCache = {}

    @property
    def params(self):
        return list(self.paramsModel.displayNames)

    @property
    def tex(self):
        return self.paramsModel.tex

    def _update_triangle(self, post=None):
        if post is None:
            post = lambda x: x

        # An educational moment. Proof matplotlib is bad
        # get_ in python is redundant, 
        # I already know that it's a figure (no thanks to duck typing)
        # fig_height or figHeight are both equal in being better than figheight
        # three idiotic mistakes that had forever to get fixed. => matplotlib = bad
        # QED
        figsize = self.triCanvas.figure.get_figwidth(), self.triCanvas.figure.get_figheight()

        # Another educational moment. You would think that this is enough.
        # figsize = self.triCanvas.get_width_height()
        fig = updateTrianglePlot(plt.figure(figsize=figsize), self.params, self.tex,
                                 self.samples, self.legends, post)
        self.triCanvas.figure = fig
        fig.set_canvas(self.triCanvas)
        self.triCanvas.draw_idle()
        self._update_higson()

    def _update_higson(self):
        fig = self.higCanvas.figure
        fig.clear()
        ax = fig.gca()
        ax.set_xlabel(r'$\log X$')
        ax.set_ylabel(r'$LX$')
        for x in self.samples:
            with np.errstate(divide='ignore'):
                logX = np.log(self.samples[x].nlive / (self.samples[x].nlive+1)).cumsum()
            LX = self.samples[x].logL/self.beta + logX
            LX = np.exp(LX-LX.max())
            ax.plot(logX, LX, color=self.legends[x].color)
        self.higCanvas.draw_idle()

    @QtCore.Slot()
    @QtCore.Slot(object, object)
    def invalidateCache(self, *args):
        self._LCache = {}

    def _cache_figure(self, logL, *args):
        self._LCache[self.logL] = self.triCanvas.figure
        self.logL = logL
        if self.logL in self._LCache:
            self.triCanvas.figure = self._LCache[self.logL]
            self._LCache[self.logL].set_canvas(self.triCanvas)
            self.triCanvas.draw_idle()
        else:
            self._update_triangle(lambda x: x.live_points(self.logL))
            self._LCache[self.logL] = self.triCanvas.figure

    def _cache_rgb(self, logL, *args):
        print('caching what we have')
        rgb = self.triCanvas.tostring_rgb()
        ncols, nrows = self.triCanvas.get_width_height()
        self._LCache[self.logL] = np.fromstring(rgb, dtype=np.uint8).reshape(nrows, ncols, 3)
        self.logL = logL
        if self.logL in self._LCache:
            print(f're-using for {self.logL}')
            ax = self.triCanvas.figure.gca()
            ax.imshow(self._LCache[self.logL])
            self.triCanvas.draw_idle()
        else:
            print(f'drawing {self.logL}')
            self._update_triangle(lambda x: x.live_points(self.logL))
        
    @QtCore.Slot(float)
    def changeLogL(self, logL, *args):
        self._cache_figure(logL, *args)
        # self._cache_rgb(logL, *args)

    @QtCore.Slot(float)
    def changeTemperature(self, beta, *args):
        self.beta = beta
        self._update_triangle()
        self._update_higson()

    @QtCore.Slot()
    @QtCore.Slot(object)
    @QtCore.Slot(object, object)
    def reDraw(self, samples=None, legends=None, *args):
        print(samples, legends)
        if samples is not None and not isinstance(samples, QtCore.QModelIndex):
            self.samples = samples
        if legends is None:
            if self.legends is None:
                for k in self.samples:
                    self.legends[k] = Legend(title=k)
        else:
            # Fuck the Duck typing. 
            if not isinstance(legends, QtCore.QModelIndex):
                self.legends = legends
        self.notify.emit('Full repaint...')
        self._update_triangle()
        self._update_higson()
        self.notify.emit('Fully repainted.')


def updateTrianglePlot(figure, params, tex, samples, legends, postprocess):
    figure.clear()
    figure, axes = make_2d_axes(params, tex=tex, fig=figure, upper=False)
    for x in samples:
        postprocess(samples[x])\
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

