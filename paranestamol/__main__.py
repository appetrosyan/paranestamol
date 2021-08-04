#!/usr/bin/env python
r"""This is the main file for invoking the paranestamol application."""
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
    """Self-explanatory."""
    parser = argparse.ArgumentParser(
        prog='paranestamol',
        description="Paranestamol, graphical nested sampling visualisation.",
        usage='python3 -m %(prog)s [options]')
    parser.add_argument('file_roots',
                        metavar='file root(s)',
                        type=str,
                        nargs='*',
                        help='file_root to process')
    return parser.parse_args()


def app_setup(name):
    """Housekeeping boilerplate."""
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

    engine = QtQml.QQmlApplicationEngine(parent=app)
    context = engine.rootContext()
    paramsModel = ParameterModel(parent=app)
    samplesModel = SamplesModel(parent=app)
    trianglePlotter = TrianglePlotter(paramsModel, parent=engine)

    context.setContextProperty("trianglePlotter", trianglePlotter)
    proxy = QtCore.QSortFilterProxyModel()
    proxy.setSourceModel(paramsModel)
    proxy.setFilterRole(ParameterModel.nameRole)
    context.setContextProperty('paramsModel', proxy)
    context.setContextProperty("samplesModel", samplesModel)

    qmlFileRoot = str(Path(Path.cwd(), Path(__file__).parent, "view.qml"))
    engine.addImportPath(PROJECT_PATH)
    engine.load(qmlFileRoot)

    win = engine.rootObjects()[0]
    trianglePlotter.triCanvas = win.findChild(QtCore.QObject, "trianglePlot")
    trianglePlotter.higson.canvas = win.findChild(QtCore.QObject, "higsonPlot")
    trianglePlotter.notify.connect(win.displayPythonMessage)
    samplesModel.notify.connect(win.displayPythonMessage)
    samplesModel.fullRepaint.connect(trianglePlotter.reDraw)
    samplesModel.newParams.connect(paramsModel.addParams)
    paramsModel.dataChanged.connect(trianglePlotter.reDraw)
    paramsModel.dataChanged.connect(trianglePlotter.invalidateCache)

    temperatureSlider = win.findChild(QtCore.QObject, "temperature_slider")
    temperatureSlider.valueChangeStarted\
                     .connect(trianglePlotter.changeTemperature)
    loglSlider = win.findChild(QtCore.QObject, "logl_slider")
    loglSlider.valueChangeStarted.connect(trianglePlotter.changeLogL)

    for file_root in args.file_roots:
        try:
            samplesModel.appendRow(file_root)
        except FileNotFoundError as err:
            samplesModel.notify.emit(f"Error: {err}")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
