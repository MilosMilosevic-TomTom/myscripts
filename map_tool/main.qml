import QtQuick 2.12
import QtQuick.Layouts 1.12

import QtQuick.Controls 2.5
import QtLocation 5.12
import QtPositioning 5.12

ApplicationWindow {
    id: window
    visible: true
    width: 1024
    height: 768
    title: qsTr("Map Tool")
    Plugin {
        id: mapPlugin
        name: "osm" // "mapboxgl", "esri", ...
    }

    Map {
        anchors.fill: parent
        id: mapView

        plugin: mapPlugin
        center: QtPositioning.coordinate(59.91, 10.75) // Oslo

        property var defaultZoomLevel: 20.
        property var lineSource: null
        property var lineTarget: null
        property var lineCombined: null
        property var lineJoins: null

        function getPos(point) {
            return QtPositioning.coordinate(point.latitude, point.longitude)
        }

        function detachLine(line) {
            if (null !== line) {
                line.removeFromMap(mapView)
            }
        }

        function createLine(drift, path, width, color, opacity) {

            if (null !== path) {
                var lineComponent = Qt.createComponent("qrc:///TheLine.qml")

                if (lineComponent.status === Component.Ready) {
                    var obj = lineComponent.createObject(null, {
                                                             "line.width": width,
                                                             "line.color": color,
                                                             "marker_drift": drift,
                                                             "opacity": opacity,
                                                             "path": path
                                                         })

                    if (obj === null) {
                        // Error Handling
                        console.log("Error creating object",
                                    lineComponent.errorString())
                    } else {
                        obj.addToMap(mapView)
                        return obj
                    }
                } else {
                    console.log("Error: ", lineComponent.status,
                                lineComponent.errorString())
                }
            }

            return null
        }

        function createJoinsGroup(width, color, opacity) {

            var lineComponent = Qt.createComponent("qrc:///JoinsCollection.qml")
            if (lineComponent.status === Component.Ready) {
                var obj = lineComponent.createObject(null, {
                                                         "jwidth": width,
                                                         "jcolor": color,
                                                         "jopacity": opacity
                                                     })

                if (obj === null) {
                    // Error Handling
                    console.log("Error creating object",
                                lineComponent.errorString())
                } else {
                    return obj
                }
            } else {
                console.log("Error: ", lineComponent.status,
                            lineComponent.errorString())
            }

            return null
        }

        function evalPolylinesAndCopy(js_code) {
            //those names must be exactly same as pasted in text box or "fixed" by mainqml.cpp code
            //those are filled by eval
            var sourcePolyline = null
            var targetPolyline = null
            var combinedPolyline = null
            var indexMapping = null
            var sourceSegments = null
            var targetSegments = null

            eval(js_code)

            const convertPoly = function (poly) {
                var res = "{"
                if (null !== poly) {
                    for (var i in poly) {
                        res += "ToLatLon(" + poly[i].latitude + ", " + poly[i].longitude + "), "
                    }
                }
                res += "};"

                return res
            }

            const convertSegments = function (segments) {
                var res = "{"
                if (segments !== null) {
                    for (var i in segments) {
                        res += "{" + segments[i].start_point_index + ", "
                                + segments[i].end_point_index
                                + ",  LegSegmentData{LegSummary::Zero()}}, "
                    }
                }

                res += "};"
                return res
            }

            const sp = "const Polyline kSourcePolyline " + convertPoly(
                         sourcePolyline)
            const tp = "const Polyline kTargetPolyline " + convertPoly(
                         targetPolyline)

            const ss = "const Segments kSourceSegments " + convertSegments(
                         sourceSegments)
            const ts = "const Segments kTargetSegments " + convertSegments(
                         targetSegments)

            main_qml.copyToClipboard(sp + "\n" + tp + "\n" + ss + "\n" + ts)
        }

        function evalPolylines(js_code) {

            //those names match to what dumper prints into tom-tom engine
            detachLine(lineSource)
            detachLine(lineTarget)
            detachLine(lineCombined)
            detachLine(lineJoins)

            //those names must be exactly same as pasted in text box or "fixed" by mainqml.cpp code
            //those are filled by eval
            var sourcePolyline = null
            var targetPolyline = null
            var combinedPolyline = null
            var indexMapping = null
            var sourceSegments = null
            var targetSegments = null

            const ToLatLon = function (x, y) {
                return {
                    "latitude": x,
                    "longitude": y
                }
            }

            const centerOn = function (line) {
                if (null !== line) {
                    mapView.center = getPos(line[0])
                    return true
                }
                return false
            }

            eval(js_code)
            const tmp = centerOn(sourcePolyline) || centerOn(targetPolyline)

            zoomControl.currentZoom = defaultZoomLevel

            lineSource = createLine(2, sourcePolyline, 2, m_lSource.color, 1.0)

            lineTarget = createLine(-7, targetPolyline, 2, m_lTarget.color, 0.6)

            if (null !== indexMapping) {
                lineJoins = createJoinsGroup(3, m_lJoins.color, 1)
                for (var i in indexMapping) {
                    var isrc = indexMapping[i].isrc
                    var itgt = indexMapping[i].itgt

                    var text = "S:" + isrc + ";T:" + itgt

                    lineJoins.addJoin(lineSource.path[isrc],
                                      lineTarget.path[itgt], text)
                }

                lineJoins.addToMap(mapView)
            }

            lineCombined = createLine(-14, combinedPolyline, 4,
                                      m_lCombined.color, 0.3)
        }

        //this is workaround of limited zoom, it can be more then 17 limit if set manually
        MouseArea {
            id: zoomControl
            anchors.fill: parent
            acceptedButtons: Qt.AllButtons
            property var currentZoom: parent.defaultZoomLevel

            onCurrentZoomChanged: {
                mapView.zoomLevel = currentZoom
            }

            onWheel: {

                wheel.accepted = 0 === wheel.modifiers
                if (wheel.accepted) {
                    currentZoom += wheel.angleDelta.y / 120.0
                }
            }

            property var controlsLeftMargin: 5.

            Button {
                id: m_btn
                anchors.top: parent.top

                anchors.left: parent.left
                anchors.leftMargin: parent.controlsLeftMargin

                text: "M"
                width: 48
                height: 48
                onClicked: {
                    drawer.open()
                }
            }

            Label {
                id: m_lSource
                anchors.top: m_btn.bottom

                anchors.left: parent.left
                anchors.leftMargin: parent.controlsLeftMargin

                text: "Source Line"
                color: 'green'
            }
            Label {
                id: m_lTarget
                anchors.top: m_lSource.bottom

                anchors.left: parent.left
                anchors.leftMargin: parent.controlsLeftMargin

                text: "Target Line"
                color: 'red'
            }
            Label {
                id: m_lCombined
                anchors.top: m_lTarget.bottom

                anchors.left: parent.left
                anchors.leftMargin: parent.controlsLeftMargin

                text: "Combined Line"
                color: 'blue'
            }

            Label {
                id: m_lJoins
                anchors.top: m_lCombined.bottom

                anchors.left: parent.left
                anchors.leftMargin: parent.controlsLeftMargin

                text: "Index Mapping"
                color: 'orange'
            }
        }
    }

    Drawer {
        id: drawer
        width: 0.66 * window.width
        height: window.height

        onHeightChanged: {
            textScroller.updateHeight()
        }

        ColumnLayout {
            anchors.fill: parent
            ScrollView {
                id: textScroller
                Layout.fillWidth: true
                Layout.fillHeight: false
                Layout.alignment: Qt.AlignLeft | Qt.AlignTop
                ScrollBar.horizontal.policy: ScrollBar.AlwaysOn
                ScrollBar.vertical.policy: ScrollBar.AlwaysOn
                clip: true
                TextArea {
                    id: sourceData
                    font.pointSize: 10
                    wrapMode: TextEdit.WordWrap
                    clip: true
                    placeholderText: qsTr("Add dumped JS like:\nconst onlinePolyline = [{ lat: 48.133830, lng: 11.568140},{ lat: 48.133780, lng: 11.567820}];")
                }

                function updateHeight() {
                    Layout.minimumHeight = drawer.height - parent.getButtonsHeightTotal()
                    Layout.maximumHeight = Layout.minimumHeight
                }
            }

            function getButtonsHeightTotal() {
                return btnRebuild.height + btnCopy.height
            }

            Button {
                id: btnRebuild

                Layout.maximumHeight: 48
                Layout.minimumHeight: 48
                Layout.fillHeight: false
                Layout.fillWidth: true

                Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom
                text: qsTr("Put JS from above to the map below.")
                onClicked: {
                    drawer.close()
                    mapView.evalPolylines(main_qml.textToMap(sourceData.text))
                }
            }

            Button {
                id: btnCopy

                Layout.maximumHeight: 48
                Layout.minimumHeight: 48
                Layout.fillHeight: false
                Layout.fillWidth: true

                Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom
                text: qsTr("Copy source/target parsed as C++ code.")
                onClicked: {
                    mapView.evalPolylinesAndCopy(main_qml.textToMap(
                                                     sourceData.text))
                }
            }
        }
    }
    Component.onCompleted: {
        showMaximized()
        zoomControl.currentZoom = mapView.defaultZoomLevel
        textScroller.updateHeight()
        drawer.open()
    }
}
