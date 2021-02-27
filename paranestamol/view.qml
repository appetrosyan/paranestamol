import QtQuick 2.12
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
			loadWindow.fileModel.appendRow(loadWindow.fileName)
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
			id: pageIndicator
			count: mainView.count
			visible: samplesView.visible
			currentIndex: mainView.currentIndex
			anchors.verticalCenter: parent.verticalCenter
			anchors.horizontalCenter: parent.horizontalCenter
			interactive: true
		}
		ToolButton {
			visible: mainView.itemAt(mainView.currentIndex+1) &&
				mainView.itemAt(mainView.currentIndex + 1).visible
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
		interactive: pageIndicator.visible
		Page{
			title: qsTr("Load Samples")
			LoadWindow{
				id: loadWindow
				fileModel: samplesModel
				anchors.fill: parent
				onBrowseForFile:{
					fileBrowse.visible=true
				}
				onRequestLoadSamples:{
					fileModel.appendRow(filename)
					samplesView.visible = true
				}
				anchors.centerIn: parent
				anchors.leftMargin: 8
				anchors.rightMargin: 8
				anchors.topMargin: 8
				anchors.bottomMargin: 8
			}
		}
		Page {
			id: samplesView
			title: qsTr("View Samples")
			visible: !samplesModel.isEmpty
			FigureCanvas {
				id: triangleView
				height: parent.height - higson.height - 40 
				width: parent.width - temperature.width 
				objectName : "trianglePlot"
			}
			Manipulator{
				id: temperature
				from: 0
				to: 10
				stepSize: 0.2
				objectName: 'temperature_slider'
				text: 'beta'
				trans: a => Math.exp(a)
				invtrans: a => Math.log(a)
				orientation: Qt.Vertical
				width: 60
				anchors.right: parent.right
				anchors.top: parent.top
				anchors.bottom: parent.bottom
			}
			Manipulator{
				id: logL
				from: samplesModel.minLogL
				stepSize: (-1 - samplesModel.minLogL)/60
				to: -1
				value: -1
				objectName: 'logl_slider'
				text: 'logL'
				height: 40
				anchors.left: parent.left
				anchors.right: temperature.left
				anchors.bottom: higson.top
			}
			FigureCanvas{
				id: higson
				height: 100
				anchors.left: parent.left
				anchors.bottom: parent.bottom
				anchors.right: temperature.left
				objectName: 'higsonPlot'
			}
			Button{
				anchors.topMargin: 8
				anchors.leftMargin: 14
				anchors.top: triangleView.top
				anchors.left: triangleView.left
				width: 50
				height: 50
				text: '⋮'
				onClicked: {
					paramsPopup.visible = true
				}
				Popup{
					id: paramsPopup
					width: 250
					height: 300
					TextField{
						id: filter
						width: parent.width
						placeholderText: qsTr('Filter')
						onTextChanged: paramsModel.setFilterFixedString(text)
					}
					ListView{
						id: paramView
						model: paramsModel
						anchors.top: filter.bottom
						anchors.right: parent.right
						anchors.bottom: parent.bottom
						anchors.left: parent.left
						header:	Item{
							anchors.left: parent.left
							anchors.right: parent.right
							height: childrenRect.height
							Column{
								height: childrenRect.height
								anchors.left: parent.left
								anchors.right: parent.right
								PlotSelector{
									type: "lower"
									anchors.left: parent.left
									anchors.right: parent.right
									onNewTypeChosen: {
										displayBridge.lowerType = value
									}
									currentIndex: 2 // Scatter
								}
								PlotSelector{
									type: "diagonal"
									anchors.left: parent.left
									anchors.right: parent.right
									onNewTypeChosen: {
										displayBridge.diagonalType = value
									}
									currentIndex: 0 // Hist
								}
							}
						}
						delegate: Component{
							Item{
								height: selectedBox.height
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
		anchors.left: parent.left
		anchors.leftMargin: 8
	}
}

