import QtQuick.Controls 2.12
import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Dialogs 1.0


ColumnLayout{
	property var fileModel
	property alias fileName: fileRootBox.text
	signal browseForFile()
	signal requestLoadSamples(string filename)
	ColorDialog{
		id: colorBrowse
		title: qsTr("Please select legend color")
		visible: false
	}
	
	width: 500
	height: 200
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
				browseForFile()
			}
			text: qsTr("Browse...")
		}
	}
	Rectangle{
		id: fileViewRect
		width: parent.width
		height: parent.height-fileRootBox.height-loadButton.height
		border.color: "black"
		border.width: 1
		ListView{
			id: fileView
			anchors.fill: parent
			anchors.centerIn: parent
			model: fileModel
			clip: true
			delegate: Component{
				Item{
					width: parent.width
					height: childrenRect.height
					CheckBox{
						id: display
						checked: model.display
						onClicked: {
							console.log("Clicked")
						}
					}
					Rectangle{
						id: legendColor
						color: model.legend_color
						anchors.left: display.right
						anchors.verticalCenter: display.verticalCenter
						width: 10
						height: fileLine.height-2
						MouseArea {
							anchors.fill: parent
							signal updaColor()
							onUpdaColor:{
								console.log(colorBrowse.color)
								model.legend_color = colorBrowse.color
							}
							onClicked: {
								fileView.currentIndex = index
								colorBrowse.visible = true
								colorBrowse.accepted.connect(this.updaColor)
							}
							
						}
					}
					TextInput{
						id: fileLine
						anchors.left: legendColor.right
						anchors.verticalCenter: legendColor.verticalCenter
						text: model.legend_name
						width: 100
						onAccepted:{
							model.legend_name = text
							text = model.legend_name
						}
					}
					Text{
						id: pathLine
						anchors.top: fileLine.bottom
						anchors.right: parent.right
						text: model.url
						elide: Text.ElideLeft
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
	Button{
		id: loadButton
		onClicked:{
			requestLoadSamples(fileRootBox.text)
		}
		text: qsTr("Load samples")
	}
}

