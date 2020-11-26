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
	id: mainWindow
	visible: true
	title: mainView.currentItem.title
	width: 800
	minimumWidth: 400
	height: 600
	minimumHeight: 200
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
			loadWindow.fileModel.appendRow(fileName)
		}
	}
	header: ToolBar{
		visible: mainWindow.height > 400
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
				anchors.top: parent.top
				implicitWidth: 700
				height: 400
				objectName : "trianglePlot"
			}
			Manipulator{
				id: temperature
				from: -5
				to: 10
				stepSize: 1
				objectName: 'temperature_slider'
				text: 'beta'
				trans: a => Math.exp(a)
				invtrans: a=> Math.log(a)
				orientation: Qt.Vertical
				width: 60
				anchors.right: parent.right
				anchors.top: mplView.top
				anchors.bottom: mplView.bottom
			}
			Manipulator{
				id: logL
				from: -5000
				stepSize: 100
				to: -1
				objectName: 'logl_slider'
				text: 'logL'
				height: 40
				anchors.left: mplView.left
				anchors.top: mplView.bottom
				anchors.right: mplView.right
			}
			FigureCanvas{
				id: higson		/*It should be capital, but you have*/
				anchors.top: logL.bottom		 /* to follow the convention*/
				height: 100
				anchors.bottom: parent.bottom
				anchors.left: logL.left
				anchors.right: logL.right
				objectName: 'higsonPlot'
			}
			Button{
				anchors.top: mplView.top
				anchors.left: mplView.left
				width: 50
				height: 50
				text: '⋮'
				onClicked: {
					paramsPopup.visible = true
				}
				Popup{
					id: paramsPopup
					width: 200
					height: 400
					ListView{
						id: paramView
						model: paramsModel
						anchors.fill: parent 
						delegate: Component{
							Item{
								height: 80
								width: paramView.width
								CheckBox{
									id: selectedBox
									checked: model.selected
									anchors.left: parent.left
									anchors.verticalCenter: parent.verticalCenter
									onClicked: {
										model.selected = !model.selected
									}
								}
								Text {
									anchors.left: selectedBox.right
									anchors.right: parent.right
									anchors.verticalCenter: parent.verticalCenter
									text: model.name
									color: Material.foreground
								}
							}
						}
						ScrollIndicator.vertical: ScrollIndicator{
							parent: paramView.parent
							anchors.top: paramView.top
							anchors.bottom: paramView.bottom
							anchors.right: paramView.right
						}
						clip: true
					}
				}
			}
		}
	}
	footer: Text{
		id: statusBar
		text: "Status"
		color: Material.foreground
		font.bold: true
	}
}

