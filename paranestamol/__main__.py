#!/usr/bin/env python
r"""This is the main file for invoking the paranestamol binary. If you
want to adjust the QML with live updates, please use `python3 -m
paranestamol --live` as your invocation.

"""
import sys
import signal
import os
import argparse
from pathlib import Path
from matplotlib_backend_qtquick.backend_qtquickagg import FigureCanvasQtQuickAgg
from matplotlib_backend_qtquick.qt_compat import QtGui, QtQml, QtCore, QtWidgets

from .samples_model import SamplesModel, ParameterModel
from .plt_managers import TrianglePlotter

PROJECT_PATH = os.path.dirname(os.path.realpath(__name__))


class MyApp(QtCore.QObject, object):
    def __init__(self, live, parent=None, engine=None, rootFile='./main.qml'):
        super(MyApp, self).__init__(parent)
        self.engine = QtQml.QQmlApplicationEngine() if engine is None else engine
        self.engine.addImportPath(PROJECT_PATH)
        if live:
            try:
                from livecoding import start_livecoding_gui
                start_livecoding_gui(self.engine, PROJECT_PATH, __file__, live_qml=rootFile)
            except ImportError:
                print("Cannot do Live coding. ")
                sys.exit()
        else:
            self.engine.load(rootFile)
        self._start_check_timer()

    def _start_check_timer(self):
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(lambda: None)
        self._timer.start(100)   

def parse_args():
    parser = argparse.ArgumentParser(
        description="""Paranestamol, the graphical nested sampling visualisation script."""
    )
    parser.add_argument(
        '-l',
        '--live',
        help='Start the application in live editing mode', action='store_true'
    )
    return parser.parse_args()


def appSetup(name):
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName(f"{name}")
    app.setOrganizationDomain(f"{name}.org")
    app.setApplicationName(f"{name}")
    return app

def main():
    signal.signal(signal.SIGINT, lambda *args: QtWidgets.QApplication.quit())
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = appSetup("Paranestamol")
    QtQml.qmlRegisterType(FigureCanvasQtQuickAgg, "Backend", 1, 0, "FigureCanvas")
    args = parse_args()

    engine = QtQml.QQmlApplicationEngine()
    context = engine.rootContext()
    displayBridge = TrianglePlotter()
    paramsModel = ParameterModel()
    samplesModel = SamplesModel()
    displayBridge.paramsModel = paramsModel



    context.setContextProperty("displayBridge", displayBridge)
    context.setContextProperty('paramsModel', paramsModel)
    context.setContextProperty("samplesModel", samplesModel)

    qmlFileRoot =str(Path(Path.cwd(), Path(__file__).parent, "view.qml"))
    gui = MyApp(live=args.live, engine=engine, rootFile=qmlFileRoot)
    
    win = gui.engine.rootObjects()[0]
    displayBridge.triCanvas = win.findChild(QtCore.QObject, "trianglePlot")
    displayBridge.higCanvas = win.findChild(QtCore.QObject, "higsonPlot")

    displayBridge.notify.connect(win.displayPythonMessage)
    samplesModel.notify.connect(win.displayPythonMessage)
    samplesModel.fullRepaint.connect(displayBridge.reDraw)
    samplesModel.newParams.connect(paramsModel.addParams)
    paramsModel.dataChanged.connect(displayBridge.reDraw)
    paramsModel.dataChanged.connect(displayBridge.invalidateCache)

    
    temperatureSlider = win.findChild(QtCore.QObject, "temperature_slider")
    # temperatureSlider.valueChangeFinished\
    #                  .connect(displayBridge.changeTemperature)
    temperatureSlider.valueChangeStarted\
                     .connect(displayBridge.changeTemperature)
    loglSlider = win.findChild(QtCore.QObject, "logl_slider")
    loglSlider.valueChangeStarted.connect(displayBridge.changeLogL)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
