import QtQuick.Controls 2.12
import QtQuick 2.12

import "utils.js" as Utils

Item{
	property var type: "lower"
	property alias currentIndex: comboBox.currentIndex
	width: childrenRect.width
	height: childrenRect.height
	signal newTypeChosen(var value)
	Text{
		anchors.left: parent.left
		anchors.leftMargin: 8
		id: description
		text: Utils.prettyTypes[type]
		anchors.verticalCenter: comboBox.verticalCenter
	}
	ComboBox{
		id: comboBox
		model: type === "lower"?lowerAcceptableValues:diagonalAcceptableValues
		textRole: 'text'
		valueRole: 'key'
		anchors.right: parent.right
		anchors.rightMargin: 8
		anchors.left: description.right
		anchors.leftMargin: 8
		onActivated: {
			newTypeChosen(currentValue)
		}
	}
	
	ListModel{
		id: lowerAcceptableValues
		ListElement{
			key: 'kde'
			text: 'KDE'
		}
		ListElement{
			key: 'fastkde'
			text: 'Fast KDE'
		}
		ListElement{
			key: 'scatter'
			text: 'Scatter'
		}
	}
	ListModel{
		id: diagonalAcceptableValues
		ListElement{
			key: 'hist'
			text: 'Histogram'
		}
		ListElement{
			key: 'kde'
			text: 'KDE'
		}
	}
}

