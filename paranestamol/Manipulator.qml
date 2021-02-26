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
	Text{
		id: marker
		width: 30
		Component.onCompleted: {
			if (slider.orientation === Qt.Horizontal) {
				anchors.left = parent.left
				anchors.leftMargin = 8
				anchors.verticalCenter = parent.verticalCenter
			} else {
				anchors.topMargin = 8
				anchors.top = parent.top
				anchors.topMargin = 8
				anchors.horizontalCenter = parent.horizontalCenter
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
			if (orientation === Qt.Horizontal){
				anchors.left = marker.right
				anchors.leftMargin = 4
				anchors.right = currentValue.left
				anchors.rightMargin = 8
				anchors.verticalCenter = marker.verticalCenter
			} else {
				anchors.top = marker.bottom
				anchors.topMargin = 8
				anchors.horizontalCenter = marker.horizontalCenter // Why doesn't this FUCKING WORK!
				anchors.bottom = currentValue.top
				anchors.bottomMargin = 8
			}
		}
	}
	TextInput{
		id: currentValue
		text: "%1".arg(Math.round(trans(slider.value)))
		font.bold: focus
		property var value: trans(slider.value)
		onTextChanged: {
			valueChangeStarted(parseInt(text))
		}
		onAccepted: {
			slider.value = invtrans(parseFloat(text))
			valueChangeFinished(parseInt(text))
		}
		Component.onCompleted: {
			if (slider.orientation === Qt.Horizontal){
				anchors.right = parent.right
				anchors.rightMargin = 8
				anchors.verticalCenter = slider.verticalCenter
			} else {
				anchors.bottom = parent.bottom
				anchors.horizontalCenter = parent.horizontalCenter
			}
		}
	}
}

