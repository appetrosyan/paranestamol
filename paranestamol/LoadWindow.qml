import QtQuick.Controls 2.12
import QtQuick 2.15
import QtQuick.Layouts 1.12
import QtQuick.Dialogs 1.0



Item{
	SystemPalette {
		id: palette
		colorGroup: SystemPalette.Active
	}
	SystemPalette{
		id: disabledPalette
		colorGroup: SystemPalette.Disabled
	}
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
	RowLayout{
		id: fileRow
		width: parent.width
		TextField{
			id: fileRootBox
			Layout.fillWidth: true
			selectByMouse: true
			placeholderText: qsTr("Start by providing the path to samples' file_root")
			onTextChanged: {
				text= text.replace(/^(file:\/{2})|(qrc:\/{2})|(http:\/{2})/,"")
				var cleanPath = decodeURIComponent(text)
				fileName = cleanPath
			}
		}
		
		Button{
			id: browseButton
			onClicked: {
				browseForFile()
			}
			text: qsTr("Browse...")
		}
		Button{
			id: loadButton
			visible: fileRootBox.text!==''
			onClicked:{
				requestLoadSamples(fileRootBox.text)
			}
			text: qsTr("Load samples")
		}
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
		anchors.top: fileRow.bottom
		width: parent.width
		height: parent.height-fileRow.height
		border.width: 1
		ListView{
			id: fileView
			anchors.fill: parent
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
					property bool selected: fileView.currentIndex === index
					MouseArea{
						anchors.fill: parent
						onClicked: fileView.currentIndex = index
					}
					width: parent.width
					height: childrenRect.height
					CheckBox{
						id: display
						checked: model.display
						onClicked: {
							model.display = !model.display
						}
						anchors.verticalCenter: fileLine.verticalCenter
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
						anchors.rightMargin: 8
						wrapMode: TextInput.Wrap
						text: model.legend_name
						width: 100
						font.bold: true
						font.pointSize: 16
						color: selected? palette.highlightedText: palette.text
						onTextEdited: fileView.currentIndex = index
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
						color: selected? palette.highlightedText: palette.text
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
						color: selected? palette.highlightedText: palette.text
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
				anchors.top: fileView.currentItem.top
				anchors.bottom: fileView.currentItem.bottom
				width: fileView.currentItem.width
				color: palette.highlight
			}
			highlightFollowsCurrentItem: true
			focus: true
			Text{
				text: qsTr("<i> Empty </i>")
				anchors.centerIn: parent
				visible: fileModel.isEmpty
				color: disabledPalette.text
			}
		}
		
	}
	
}

