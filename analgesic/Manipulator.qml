import QtQuick 2.12
import QtQuick.Controls 2.12

Item{
	signal valueChangeStarted(var value)
	signal valueChangeFinished(var value)
	property alias text: marker.text
	property alias live: slider.live
	property alias from: slider.from
	property alias to: slider.to
	property alias orientation: slider.orientation
	property alias stepSize: slider.stepSize
	Text{
		id: marker
		anchors.top: parent.top
		anchors.horizontalCenter: parent.horizontalCenter
	}
	TextInput{
		id: currentValue
		text: slider.value
		onAccepted: {
			slider.value = text
		}
		anchors.top: marker.bottom
		anchors.horizontalCenter: parent.horizontalCenter
	}
	Slider{
		id: slider
		live: false
		from: 0
		to: 100
		orientation: Qt.Horizontal
		anchors.top: currentValue.bottom
		anchors.bottom: parent.bottom
		anchors.horizontalCenter: parent.horizontalCenter
		stepSize: 1
		onMoved:{
			valueChangeStarted(slider.value)
		}
		onValueChanged: {
			valueChangeFinished(currentValue.placeholderText)
		}
		
	}
}

