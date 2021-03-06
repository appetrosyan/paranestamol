import os
from paranestamol.utils import Legend, cleanupFileRoot

os.environ['QT_API'] = 'PySide2'
# This is not an unused import. This is because Python has the Zen
# statement of "There should be (preferably) one obvious way to do
# things" that roughly translates to "There should be at least two
# different ways to do one thing. The more obvious way(s) should be
# wrong, incompatible or somehow deficient but in a non-obvious
# manner. " Why can't you agree on keeping *one* backend to Qt?
from matplotlib_backend_qtquick.backend_qtquickagg import FigureCanvasQtQuickAgg as FigureCanvasQML
from matplotlib_backend_qtquick.qt_compat import QtQml, QtGui, QtWidgets, QtCore
