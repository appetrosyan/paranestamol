import os
from paranestamol.utils import Legend, cleanupFileRoot

if os.getenv('QT_API') != "PySide2":
    raise RuntimeError(f'TL;DR \n\n`QT_API=PySide2 python3 -m paranestamol `\n\n The moron who\
 designed `matplotlib_backend_qtquick` hard-coded a preference for\
 pyqt5 for their backend, despite supporting PySide2 full well. \nAdd\
 this to your .basrc file as a workaround, or better yet, inconvenience\
 said moron at https://github.com/jmitrevs/matplotlib_backend_qtquick')


# This is not an unused import. This is because Python has the Zen
# statement of "There should be (preferably) one obvious way to do
# things" that roughly translates to "There should be at least two
# different ways to do one thing. The more obvious way(s) should be
# wrong, incompatible or somehow deficient but in a non-obvious
# manner. " Why can't you agree on keeping *one* backend to Qt?

from matplotlib_backend_qtquick.backend_qtquickagg import FigureCanvasQtQuickAgg as FigureCanvasQML
from matplotlib_backend_qtquick.qt_compat import QtQml, QtGui, QtWidgets, QtCore
