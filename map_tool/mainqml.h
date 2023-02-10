#pragma once

#include <QObject>
#include <QString>
#include <QGeoCoordinate>

class MainQml : public QObject
{
    Q_OBJECT
public:
    explicit MainQml(QObject *parent = nullptr);

public slots:
    QString textToMap(QString text);
    QGeoCoordinate midPoint(const QGeoCoordinate& posA, const QGeoCoordinate& posB);
    void copyToClipboard(const QString& text);
signals:
};

