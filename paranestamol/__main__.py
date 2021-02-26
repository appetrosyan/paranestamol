#!/usr/bin/env python
r"""This is the main file for invoking the paranestamol application.

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

def parse_args():
    parser = argparse.ArgumentParser(
        prog='paranestamol',
        description="""Paranestamol, the graphical nested sampling visualisation script.""",
        usage='python3 -m %(prog)s [options]'
    )
    parser.add_argument(
        'file_roots', metavar='file root(s)', type=str, nargs='*', help='Add the following file to the file root'
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
    paramsModel = ParameterModel()
    samplesModel = SamplesModel()
    displayBridge = TrianglePlotter(paramsModel)

    context.setContextProperty("displayBridge", displayBridge)
    proxy = QtCore.QSortFilterProxyModel()
    proxy.setSourceModel(paramsModel)
    proxy.setFilterRole(ParameterModel.nameRole)
    context.setContextProperty('paramsModel', proxy)
    context.setContextProperty("samplesModel", samplesModel)

    qmlFileRoot = str(Path(Path.cwd(), Path(__file__).parent, "view.qml"))
    engine.addImportPath(PROJECT_PATH)
    engine.load(qmlFileRoot)

    win = engine.rootObjects()[0]
    displayBridge.triCanvas = win.findChild(QtCore.QObject, "trianglePlot")
    displayBridge.higCanvas = win.findChild(QtCore.QObject, "higsonPlot") 
    displayBridge.notify.connect(win.displayPythonMessage)
    samplesModel.notify.connect(win.displayPythonMessage)
    samplesModel.fullRepaint.connect(displayBridge.reDraw)
    samplesModel.newParams.connect(paramsModel.addParams)
    paramsModel.dataChanged.connect(displayBridge.reDraw)
    paramsModel.dataChanged.connect(displayBridge.invalidateCache)

    temperatureSlider = win.findChild(QtCore.QObject, "temperature_slider")
    temperatureSlider.valueChangeStarted\
                     .connect(displayBridge.changeTemperature)
    loglSlider = win.findChild(QtCore.QObject, "logl_slider")
    loglSlider.valueChangeStarted.connect(displayBridge.changeLogL)

    for x in args.file_roots:
        try:
            samplesModel.appendRow(x)
        except FileNotFoundError as e:
            print(f'{e}', file=sys.stderr)
            samplesModel.notify.emit(f"Error: {e}")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
