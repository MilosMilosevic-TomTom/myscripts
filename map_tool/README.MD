

This program allows to visualize javascipt dumps using "eval()" without checks, please ensure you don't paste harmfull code there.
Program allows to copy some data as C++ arrays to make tests for navkit-2.


Recognized array names:

Next 3 are polylines expressed as lat / lng (can use "latitude", "longitude" too):

sourcePolyline = [{lat: 1., lng: 2.}, ]
(AKA onlinePolyline)

targetPolyline
(AKA onboardPolyline)

combinedPolyline

This one is mapping of INDEXES (zero-based) between source and target arrays above, if present it will draw connection lines
indexMapping = [{isrc: 0, itgt: 2}, {isrc:10, itgt: 20}]

Recognized but not used yet:
sourceSegments 
targetSegments


Recognized C++ code:

"const Polyline ": "kOnboardPolyline", "kOnlinePolyline", "kTargetPolyline", "kSourcePolyline"
Expected syntax which will be properly recognized:

 const Polyline kTargetPolyline{
        ToLatLon(52.52709288, 13.44986661),
        ToLatLon(52.52704561, 13.44969571),
        ToLatLon(52.52696514, 13.44941676),
        ToLatLon(52.52748549, 13.44917536),  
        ToLatLon(52.52748993, 13.44917997), 
        ToLatLon(52.52696514, 13.44941676),
        ToLatLon(52.5268954, 13.44914854),
        ToLatLon(52.52671997, 13.44848),
        ToLatLon(52.52670765, 13.44843507),
        ToLatLon(52.52650917, 13.44776988),
        ToLatLon(52.52663791, 13.44761968),
        ToLatLon(52.52672911, 13.44751775),
        ToLatLon(52.52695978, 13.44726562),
        ToLatLon(52.52711996, 13.44708994),
    };

Same syntax will be used when back-copy data as C++ source.

Packages for Ubuntu:

qtbase5-dev
qtpositioning5-dev
qtdeclarative5-dev
qtlocation5-dev
qtquickcontrols2-5-dev

Possible some others, whatever compiler will say missing.
All packages are installed using apt install from the default repos.


How to use:

Press "M" button on left top of the window (or left swipe). That will open text field to paste source, it has 2 buttons - draw and copy as C++.
Mouse gestures on map correspond to standard Qt behaviour of OSMP maps. Try shift/ctrl etc. Except zoom is allowed any while standard blocks at 17.

Additional C++ code included in folder "addition" to make dumping easier from navkit-2.
