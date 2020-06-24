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
from .plt_managers import TrianglePlotter


def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    sys.argv += ['--style', 'material']
    app = QtGui.QGuiApplication(sys.argv)
    engine = QtQml.QQmlApplicationEngine()
    displayBridge = TrianglePlotter()
    context = engine.rootContext()
    context.setContextProperty("displayBridge", displayBridge)
    samplesModel = SamplesModel()
    samplesModel.fullRepaint.connect(displayBridge.reDraw)
    context.setContextProperty("samplesModel", samplesModel)
    QtQml.qmlRegisterType(FigureCanvasQtQuickAgg,
                          "Backend", 1, 0, "FigureCanvas")
    qmlFile = Path(Path.cwd(), Path(__file__).parent, "view.qml")
    engine.load(QtCore.QUrl.fromLocalFile(str(qmlFile)))
    win = engine.rootObjects()[0]
    displayBridge.notify.connect(win.displayPythonMessage)
    samplesModel.notify.connect(win.displayPythonMessage)

    displayBridge.canvas = win.findChild(QtCore.QObject, "trianglePlot")
    displayBridge.figure = displayBridge.canvas.figure
    app.exec_()


if __name__ == "__main__":
    main()
