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
			visible: mainView.itemAt(mainView.currentIndex-1)
			text: visible?mainView.itemAt(mainView.currentIndex-1).title:''
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
			visible: mainView.itemAt(mainView.currentIndex+1)
			text: visible?mainView.itemAt(mainView.currentIndex+1).title:''
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
			title: "Load Samples"
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
			title: "View Samples"
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
			Manipulator{
				id: temperature
				from: 0
				to: 100
				stepSize: 1
				objectName: 'temperature_slider'
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
				objectName: 'logl_slider'
				text: 'logL'
				anchors.left: mplView.left
				anchors.top: mplView.bottom
				anchors.bottom: parent.bottom
				anchors.right: mplView.right
			}
			Button{
				anchors.top: mplView.top
				anchors.left: mplView.left
				width: 50
				height: 50
				text: '⋮'
				onClicked: {
					legendPopup.visible = true
					console.log(paramsModel)
				}
				Popup {
					id: legendPopup
					width: 300
					height: 300
					ListView {
						id: outerView
						model: paramsModel
						delegate: Component  {
							Item{
								height: childrenRect.height
								width: parent.width
								Text{
									text: model.name
									color: Material.foreground
								}
							}
						}
						anchors.fill: parent 
					}
					
				}
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
