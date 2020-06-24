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
	Material.theme: Material.Dark
	Material.accent: Material.Orange
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
			loadWindow.fileModel.appendRow(cleanPath)
		}
	}
	header: ToolBar{
		ToolButton {
			text: "￩"
			onClicked: {
				mainView.decrementCurrentIndex()
			}
			anchors.left: parent.left
		}
		PageIndicator{
			count: mainView.count
			currentIndex: mainView.currentIndex
			anchors.verticalCenter: parent.verticalCenter
			anchors.horizontalCenter: parent.horizontalCenter
			interactive: true
		}
		ToolButton {
			text: "￫"
			onClicked: {
				mainView.incrementCurrentIndex()
			}
			anchors.right: parent.right
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
				anchors.leftMargin: 8
				anchors.right: temperature.left
				anchors.top: parent.top
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
					displayBridge.changeTemperature(this.value)
				}
				text: 'beta'
				orientation: Qt.Vertical
				width: 60
				anchors.right: parent.right
				anchors.top: mplView.top
				anchors.bottom: mplView.bottom
			}
			Manipulator{
				id: logL
				from: -100
				to: -1
				onValueChangeStarted: {
					displayBridge.changeLogL(this.value)
				}
				text: 'logL'
				anchors.left: mplView.left
				anchors.top: mplView.bottom
				anchors.bottom: parent.bottom
				anchors.right: mplView.right
			}
		}
	}

	Popup{
		x: parent.width - 308
		y: parent.height - 200
		width: 300
		height: 150
		visible: true
		transformOrigin: Popup.BottomRight
	}
	
	footer: Text{
		id: statusBar
		text: "placeholder"
		
		color: Material.foreground
		font.bold: true
	}
}
