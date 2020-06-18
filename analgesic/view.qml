import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12
import QtQuick.Dialogs 1.0
import QtQuick.Layouts 1.12
import QtGraphicalEffects 1.12

import Backend 1.0



ApplicationWindow {
	function baseName(str)
	{
		var base = new String(str).substring(str.lastIndexOf('/') + 1); 
		if(base.lastIndexOf(".") != -1)       
			base = base.substring(0, base.lastIndexOf("."));
		return base;
	}
	function loadFile(url) {
		var path=(displayBridge.loadSamples(url))
		samplesFiles.append(
			{
				'url': path,
				'name': baseName(path)
			})
		displayBridge.loadSamplesCallback(baseName(path))
	}

    id: mainWindow
    visible: true
	title: mainView.currentItem.title
    width: 800
    height: 600
	FileDialog{
		id: fileBrowse
		title: qsTr("Please choose the samples root file")
		visible: false
		folder: shortcuts.home
		onAccepted: {
			fileRootBox.text = fileBrowse.fileUrl
			fileRootBox.text = fileRootBox.text.substring(7)
		}
	}
	SwipeView{
		id: mainView
		anchors.fill: parent
		Page{
			title: qsTr("Welcome screen")
			ColumnLayout{
				width: 500
				height: 200
				anchors.centerIn: parent
				RowLayout{
					TextField{
						id: fileRootBox
						Layout.fillWidth: true
						selectByMouse: true
						placeholderText: qsTr("Path to samples `file_root`")
						text: "/Users/app/Downloads/data.1908.09139/klcdm/chains/BAO.inputparams"
					}
					Button{
						id: browseButton
						onClicked: {
							fileBrowse.visible=true
						}
						text: qsTr("Browse...")
					}
				}
				Rectangle{
					width: 500
					height: 150
					border.color: "black"
					border.width: 1
					ListView{
						id: fileView
						anchors.fill: parent
						model: samplesFiles
						delegate: Component{
							Item{
								width: fileView.width
								height: fileLine.height
								Text{
									id: fileLine
									text: model.name 
									width: 100
								}
								Text{
									anchors.right: parent.right
									text: model.url
									elide: Text.ElideLeft
									width: fileView.width - fileLine.widht
								}
								MouseArea{
									anchors.fill: parent
									onClicked: {
										fileView.currentIndex = index
									}
								}
							}
						}
						highlight: Rectangle{
							y: fileView.currentItem.y
							color: "lightsteelblue"
							radius: 5
							width: fileView.currentItem.width
							height: fileView.currentItem.height
							Behavior on y{
								SpringAnimation{
									spring: 3
									damping: 0.2
								}
							}
						}
						highlightFollowsCurrentItem: false
						focus: true
					}
				}
				ListModel{
					id: samplesFiles
				}
				Button{
					id: loadButton
					onClicked:{
						loadFile(fileRootBox.text)
					}
					text: qsTr("Load samples")
				}
			}
		}
		Page {
			title: "Sine wave view"
			FigureCanvas {
  				id: mplView
				width: 700
				height: 500
				objectName : "figure"
				
			}
			GaussianBlur{
				id: viewBlur
				anchors.fill: mplView
				visible: true
				opacity: 0
				Behavior on opacity{
					NumberAnimation{
						
					}
				}
				source: mplView
				radius: 24
				samples: 24
			}
			Slider{
				id: temperature
				live: false
				from: 0
				to: 100
				onMoved: {
					viewBlur.opacity=1
				}
				onValueChanged: {
					displayBridge.changeTemperature(value)
					viewBlur.opacity=0
				}
				orientation: Qt.Vertical
				anchors.right: parent.right
				anchors.left: mplView.right
				anchors.top: mplView.top
				anchors.bottom: mplView.bottom
			}
		}
	}
}





