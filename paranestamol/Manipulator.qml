import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Controls.Material 2.12

Item{
	signal valueChangeStarted(var value)
	signal valueChangeFinished(var value)
	property alias text: marker.text
	property alias live: slider.live
	property alias from: slider.from
	property alias to: slider.to
	property alias orientation: slider.orientation
	property alias stepSize: slider.stepSize
	property alias value: currentValue.value
	property var trans: a => a
	property var invtrans: a=>a
	Item{
		id: info
		width: Math.max(marker.width, currentValue.width)
		height: marker.implicitHeight + currentValue.implicitHeight
		Text{
			id: marker
			anchors.top: parent.top
			anchors.horizontalCenter: parent.horizontalCenter
			color: Material.foreground
			font.bold: true
		}
		TextInput{
			id: currentValue
			text: "%1".arg(Math.round(trans(slider.value)))
			font.bold: !focus
			color: focus?Material.accent:Qt.darker(Material.accent)
			property var value: trans(slider.value)
			anchors.topMargin: 20
			anchors.top: marker.bottom
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.bottom: parent.bottom
			onTextChanged: {
				valueChangeStarted(parseInt(text))
			}
			onAccepted: {
				slider.value = invtrans(parseFloat(text))
				valueChangeFinished(parseInt(text))
			}
		}
		Component.onCompleted: {
			if (slider.horizontal) {
				anchors.left = parent.left
				anchors.verticalCenter = parent.verticalCenter
				
			}
			else{
				anchors.top= parent.top
				anchors.horizontalCenter = parent.horizontalCenter
				
			}
		}
		MouseArea{
			anchors.fill: parent
			onClicked: {
				currentValue.focus=true
			}
		}
	}
	Slider{
		id: slider
		live: true
		from: 0
		to: 100
		orientation: Qt.Horizontal
		stepSize: 1
		Component.onCompleted: {
			if (horizontal){
				anchors.top = parent.top
				anchors.left = info.right
			} else {
				anchors.left = parent.left
				anchors.top = info.bottom
			}
			anchors.right = parent.right
			anchors.bottom = parent.bottom
		}
	}
}

