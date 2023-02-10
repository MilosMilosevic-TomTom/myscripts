import QtQuick 2.0

import QtQuick 2.12
import QtQuick.Layouts 1.12

import QtQuick.Controls 2.5
import QtLocation 5.12
import QtPositioning 5.12

MapPolyline {
    id: thisElement
    property var marker_drift: 0.
    property var static_text: null

    path: null

    onPathChanged: {
        addMarkersToLine()
    }
    MapItemGroup {
        id: markers
    }

    function addMarkersToLine() {
        if (null !== path) {
            var component = Qt.createComponent("map_label.qml")
            if (null !== static_text) {
                var obj1 = component.createObject(markers, {
                                                      "text": static_text,
                                                      "color": line.color,
                                                      "coordinate": main_qml.midPoint(
                                                                        path[0],
                                                                        path[1])
                                                  })
                obj1.anchorPoint.y += marker_drift
            } else {
                for (var i in path) {
                    var obj2 = component.createObject(markers, {
                                                          "text": i,
                                                          "color": line.color,
                                                          "coordinate": path[i]
                                                      })

                    obj2.anchorPoint.y += marker_drift
                }
            }
        }
    }

    function addToMap(map) {
        map.addMapItem(thisElement)
        map.addMapItemGroup(markers)
    }

    function removeFromMap(map) {
        map.removeMapItemGroup(markers)
        map.removeMapItem(thisElement)
    }
}
