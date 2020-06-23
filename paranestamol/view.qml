import QtQuick 2.12
import QtQuick.Controls.Material 2.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12
import QtQuick.Dialogs 1.0
import QtQuick.Layouts 1.12
import QtGraphicalEffects 1.12

import Backend 1.0

import "utils.js" as Utils

ApplicationWindow {
	visible: true
	title: mainView.currentItem.title
	width: 800
	minimumWidth: mainView.currentItem.implicitWidth
	height: 600
	minimumHeight: mainView.currentItem.implicitHeight
	ListModel{
		id: samplesFiles
	}
	function displayPythonMessage(msg){
		statusBar.text = msg
	}
	FileDialog{
		id: fileBrowse
		title: qsTr("Please choose the samples root file")
		visible: false
		folder: shortcuts.home
		onAccepted: {
			loadWindow.fileName = fileBrowse.fileUrl
			var path = fileBrowse.fileUrl.toString();
			path= path.replace(/^(file:\/{2})|(qrc:\/{2})|(http:\/{2})/,"");
			var cleanPath = decodeURIComponent(path);
			loadWindow.fileName = cleanPath
		}
	}
	
	SwipeView{
		id: mainView
		anchors.fill: parent
		Page{
			title: "LoadWindow"
			LoadWindow{
				id: loadWindow
				fileModel: samplesModel
				anchors.fill: parent
				onBrowseForFile:{
					fileBrowse.visible=true
				}
				onRequestLoadSamples:{
					fileModel.appendRow(filename)
				}
				anchors.centerIn: parent
				anchors.leftMargin: 8
				anchors.rightMargin: 8
				anchors.topMargin: 8
				anchors.bottomMargin: 8
			}
		}
		Page {
			title: "Nested Samples view"
			FigureCanvas {
				id: mplView
				anchors.left: parent.left
				anchors.right: temperature.left
				anchors.top: parent.top
				anchors.bottom: parent.bottom
				implicitWidth: 700
				height: 500
				objectName : "trianglePlot"
			}
			GaussianBlur{
				id: viewBlur
				anchors.fill: mplView
				source: mplView
				visible: true
				opacity: 0
				Behavior on opacity{
					NumberAnimation{

					}
				}
				radius: 24
				samples: 24
			}
			Manipulator{
				id: temperature
				from: 0
				to: 100
				stepSize: 1
				onValueChangeStarted: {
					viewBlur.opacity=1
				}
				onValueChangeFinished: {
					displayBridge.changeTemperature(value)
					viewBlur.opacity=0
				}
				text: 'beta'
				orientation: Qt.Vertical
				width: 60
				anchors.right: parent.right
				anchors.top: mplView.top
				anchors.bottom: mplView.bottom
			}
		}
	}
	PageIndicator{
		count: mainView.count
		currentIndex: mainView.currentIndex
		anchors.bottom: mainView.bottom
		anchors.horizontalCenter: mainView.horizontalCenter
		interactive: true
	}
	footer: Text{
		id: statusBar
		text: "placeholder"
	}
}
