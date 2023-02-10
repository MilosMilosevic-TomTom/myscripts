import QtQuick 2.0

import QtQuick 2.12
import QtQuick.Layouts 1.12

import QtQuick.Controls 2.5
import QtLocation 5.12
import QtPositioning 5.12

MapItemGroup {
    id: thisElement
    property var jcolor: 'white'
    property var jwidth: 1.0
    property var jopacity: 1.0
    property var arr: []

    function addJoin(cfrom, cto, static_text) {
        var lineComponent = Qt.createComponent("qrc:///TheLine.qml")
        if (lineComponent.status === Component.Ready) {
            var obj = lineComponent.createObject(null, {
                                                     "line.width": jwidth,
                                                     "line.color": jcolor,
                                                     "opacity": jopacity,
                                                     "static_text": static_text,
                                                     "path": [cfrom, cto]
                                                 })
            if (obj === null) {
                // Error Handling
                console.log("Error creating object",
                            lineComponent.errorString())
                return
            }
            arr.push(obj)
        } else {
            console.log("Error: ", lineComponent.status,
                        lineComponent.errorString())
        }
    }

    function addToMap(map) {

        //map.addMapItemGroup(thisElement)
        for (var i in arr)
            arr[i].addToMap(map)
    }

    function removeFromMap(map) {
        //map.removeMapItemGroup(thisElement)
        for (var i in arr)
            arr[i].removeFromMap(map)
    }
}
