#!/usr/bin/env python
r"""This is the main file for invoking the paranestamol application.

"""
import sys
import signal
import os
import argparse
from pathlib import Path

from paranestamol.samples_model import SamplesModel, ParameterModel
from paranestamol.plt_managers import TrianglePlotter
from paranestamol import FigureCanvasQML, QtWidgets, QtCore, QtQml


PROJECT_PATH = os.path.dirname(os.path.realpath(__name__))


def parse_args():
    """What is on the tin."""
    parser = argparse.ArgumentParser(
        prog='paranestamol',
        description="Paranestamol, graphical nested sampling visualisation.",
        usage='python3 -m %(prog)s [options]'
    )
    parser.add_argument(
        'file_roots',
        metavar='file root(s)',
        type=str, nargs='*',
        help='Add the following file to the file root'
    )
    return parser.parse_args()


def app_setup(name):
    """Housekeeping boilerplate"""
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName(f"{name}")
    app.setOrganizationDomain(f"{name}.org")
    app.setApplicationName(f"{name}")
    return app


def main():
    """Boilerplate."""
    signal.signal(signal.SIGINT, lambda *args: QtWidgets.QApplication.quit())
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = app_setup("Paranestamol")
    QtQml.qmlRegisterType(FigureCanvasQML, "Backend", 1, 0, "FigureCanvas")
    args = parse_args()

    engine = QtQml.QQmlApplicationEngine()
    context = engine.rootContext()
    paramsModel = ParameterModel()
    samplesModel = SamplesModel()
    print(samplesModel)
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
    print(temperatureSlider)
    temperatureSlider.valueChangeStarted\
                     .connect(displayBridge.changeTemperature)
    loglSlider = win.findChild(QtCore.QObject, "logl_slider")
    loglSlider.valueChangeStarted.connect(displayBridge.changeLogL)

    for file_root in args.file_roots:
        try:
            samplesModel.appendRow(file_root)
        except FileNotFoundError as err:
            print(f'{err}', file=sys.stderr)
            samplesModel.notify.emit(f"Error: {err}")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
