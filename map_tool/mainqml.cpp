#include <iostream>
#include <math.h>
#include <QClipboard>
#include <QGuiApplication>

#include "mainqml.h"

MainQml::MainQml(QObject *parent) : QObject(parent)
{

}

QString MainQml::textToMap(QString text)
{
    if (text.contains("ToLatLon", Qt::CaseSensitive))
    {
        //it was C++ code pasted, accepts copy-paste like:
        /*
        const Polyline kOnlinePolyline{
                     ToLatLon(52.51006020, 13.48002920), ToLatLon(52.50975880, 13.48096760),
                     ToLatLon(52.50868860, 13.48003690), ToLatLon(52.50781420, 13.47927240),
                     ToLatLon(52.50763980, 13.47911950), ToLatLon(52.50732330, 13.47884330), };
        */
        text.replace("const Polyline ", "", Qt::CaseSensitive);
        text.replace("kOnboardPolyline", "onboardPolyline", Qt::CaseSensitive);
        text.replace("kOnlinePolyline", "onlinePolyline", Qt::CaseSensitive);

        text.replace("kTargetPolyline", "targetPolyline", Qt::CaseSensitive);
        text.replace("kSourcePolyline", "sourcePolyline", Qt::CaseSensitive);

        text.replace("{", "[");
        text.replace("}", "]");
        if (!text.contains("="))
        {
            int j = 0;
            while ((j = text.indexOf("[", j)) != -1)
            {
                text.insert(j, "=");
                j+=2;
            }
        }

    }
    //converting from Google-Maps format to used Open Map
    text.replace("lat:", "latitude:", Qt::CaseInsensitive);
    text.replace("lng:", "longitude:", Qt::CaseInsensitive);
    text.replace("lon:", "longitude:", Qt::CaseInsensitive);
    text.replace("const", "");


    text.replace("onlinePolyline", "sourcePolyline");
    text.replace("onboardPolyline", "targetPolyline");

    //std::cout << "Button clicked: " << text.toStdString() << std::endl;

    return text;
}

template <class Float>
Float DegreesToRadians(Float degrees)
{

    constexpr static Float mul = M_PI / static_cast<Float>(180);
    return degrees * mul;
}

template <class Float>
Float RadiansToDegrees(Float radians)
{
    constexpr static Float mul = static_cast<Float>(180) / M_PI;
    return radians * mul;
}

QGeoCoordinate MainQml::midPoint(const QGeoCoordinate &posA, const QGeoCoordinate &posB)
{
    QGeoCoordinate midPoint;

    double dLon = DegreesToRadians(posB.longitude() - posA.longitude());
    double Bx = cos(DegreesToRadians(posB.latitude())) * cos(dLon);
    double By = cos(DegreesToRadians(posB.latitude())) * sin(dLon);

    midPoint.setLatitude(RadiansToDegrees(atan2(
            sin(DegreesToRadians(posA.latitude())) + sin(DegreesToRadians(posB.latitude())),
            sqrt(
                (cos(DegreesToRadians(posA.latitude())) + Bx) *
                (cos(DegreesToRadians(posA.latitude())) + Bx) + By * By))));

    midPoint.setLongitude(posA.longitude() + RadiansToDegrees(atan2(By,
                          cos(DegreesToRadians(posA.latitude())) + Bx)));

    return midPoint;
}

void MainQml::copyToClipboard(const QString &text)
{
    QClipboard *clipboard = QGuiApplication::clipboard();
    if (clipboard)
        clipboard->setText(text);
}
