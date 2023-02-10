import QtQuick 2.12
import QtQuick.Layouts 1.12

import QtQuick.Controls 2.5
import QtLocation 5.12
import QtPositioning 5.12

MapQuickItem {
    property alias text: label.text
    property alias color: label.color

    anchorPoint.x: label.width / 2
    anchorPoint.y: label.height
    //comment out zoomLevel here to keep same-sized text on zooms
    zoomLevel: 20.
    sourceItem: Label {
        id: label
    }
}
