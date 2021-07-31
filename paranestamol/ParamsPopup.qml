import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Dialogs 1.0


Item {
	id: paramsPopup
	property alias model: paramView.model
	signal saveRequested(string fileName)
	FileDialog {
		id: saveBrowse
		title: "Please select the location to save the triangle plot to."
		visible: false
		folder: shortcuts.home
		selectExisting: false
		onAccepted: {
			paramsPopup.saveRequested(fileUrl)
		}
		defaultSuffix: "png"
		nameFilters: ["Lossless Bitmap PNG (*.png)", "Lossless PDF (*.pdf)", "Lossy Bitmap JPEG (*.jpg)"]
	}
	TextField{
		id: filter
		placeholderText: qsTr('Filter')
		anchors.left: parent.left
		anchors.leftMargin: 8
		anchors.right: saveButton.left
		anchors.rightMargin: 8
		onTextChanged: paramView.model.setFilterFixedString(text)
	}
	Button {
		id: saveButton
		anchors.right: parent.right
		anchors.rightMargin: 8
		height: filter.height
		text: qsTr("Save...")
		onClicked: saveBrowse.visible = true
	}
	ListView{
		id: paramView
		anchors.top: filter.bottom
		anchors.topMargin: 4
		anchors.right: parent.right
		anchors.bottom: parent.bottom
		anchors.left: parent.left
		anchors.leftMargin: 8
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
		Component.onCompleted: {
			console.log(paramView.model)
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
					color: activePalette.text
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

