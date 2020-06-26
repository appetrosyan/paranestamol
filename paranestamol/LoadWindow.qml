import QtQuick.Controls 2.12
import QtQuick.Controls.Material 2.12
import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Dialogs 1.0


Item{
	property var fileModel
	property alias fileName: fileRootBox.text
	signal browseForFile()
	signal requestLoadSamples(string filename)
	ColorDialog{
		id: colorBrowse
		title: qsTr("Please select legend color")
		visible: false
		showAlphaChannel: true
	}
	height: 200
	TextField{
		id: fileRootBox
		anchors.top: parent.top
		anchors.left: parent.left
		anchors.right: browseButton.left
		color: Material.foreground
		anchors.rightMargin: 8
		selectByMouse: true
		placeholderText: qsTr("Path to samples `file_root`")
		onTextChanged: {
			text= text.replace(/^(file:\/{2})|(qrc:\/{2})|(http:\/{2})/,"")
			var cleanPath = decodeURIComponent(text)
			fileName = cleanPath
		}
	}
	Button{
		id: browseButton
		anchors.top: parent.top
		anchors.right: loadButton.left
		onClicked: {
			browseForFile()
		}
		text: qsTr("Browse...")
	}
	Button{
		id: loadButton
		onClicked:{
			requestLoadSamples(fileRootBox.text)
		}
		text: qsTr("Load samples")
		anchors.top: parent.top
		anchors.right: parent.right
	}
	Rectangle{
		DropArea {
			anchors.fill: parent
			onDropped :{
				fileRootBox.text = drop.text
				requestLoadSamples(fileRootBox.text)
			}
		}
		id: fileViewRect
		anchors.top: fileRootBox.bottom
		width: parent.width
		height: parent.height-fileRootBox.height-loadButton.height
		border.color: Material.foreground
		color: Material.background
		border.width: 1
		ListView{
			id: fileView
			anchors.fill: parent
			anchors.centerIn: parent
			model: fileModel
			ScrollIndicator.vertical: ScrollIndicator{
				parent: fileView.parent
				anchors.top: fileView.top
				anchors.bottom: fileView.bottom
				anchors.right: parent.right
			}
			clip: true
			delegate: Component{
				Item{
					width: parent.width
					height: childrenRect.height
					CheckBox{
						id: display
						checked: model.display
						onClicked: {
							model.display = !model.display
						}
					}
					Rectangle{
						id: legendColor
						color: model.legend_color
						opacity: model.legend_alpha
						anchors.left: display.right
						anchors.top: parent.top
						anchors.topMargin: 14
						anchors.verticalCenter: fileLine.verticalCenter
						width: 10
						MouseArea {
							anchors.fill: parent
							signal updaColor()
							onUpdaColor:{
								model.legend_color = colorBrowse.color
							}
							onClicked: {
								fileView.currentIndex = index
								colorBrowse.visible = true
								colorBrowse.color = model.legend_color
								colorBrowse.color.a = model.legend_alpha
								colorBrowse.accepted.connect(this.updaColor)
							}
							
						}
					}
					TextInput{
						id: fileLine
						anchors.top: legendColor.top
						anchors.left: legendColor.right
						anchors.leftMargin: 5
						anchors.right: parent.right
						color: Material.foreground
						wrapMode: TextInput.Wrap
						text: model.legend_name
						width: 100
						font.bold: true
						font.pointSize: 16
						onAccepted:{
							model.legend_name = text
							text = model.legend_name
						}
						Component.onCompleted:{
							fileLine.ensureVisible(0)
						}
					}
					Text{
						id: pathLine
						anchors.top: fileLine.bottom
						anchors.left: parent.left
						anchors.right: parent.right
						color: Material.foreground
						text: model.url
						leftPadding: 5
						topPadding: 5
						bottomPadding: 5
						rightPadding: 8
						horizontalAlignment: Text.AlignRight
						elide: Text.ElideRight
					}
					Text {
						id: statLine
						anchors.top: pathLine.bottom
						anchors.left: parent.left
						anchors.right: parent.right
						color: Material.foreground
						text: 'logZ: %1, D: %2, BMD: %3'.arg(model.logZ)
							.arg(model.Dkl).arg(model.bmd)
						bottomPadding: 5
						topPadding: 5
						leftPadding: 5
						rightPadding: 5
						horizontalAlignment: Text.AlignCenter
					}
				}
			}
			highlight: Rectangle{
				y: fileView.currentItem.y
				border.color: Material.accent
				color: Qt.lighter(Material.background)
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
			highlightFollowsCurrentItem: true
			focus: true
		}
	}
	
}

