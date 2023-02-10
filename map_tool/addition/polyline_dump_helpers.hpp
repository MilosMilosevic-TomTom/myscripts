/*
 * Copyright (C) 2023 TomTom NV. All rights reserved.
 *
 * This software is the proprietary copyright of TomTom NV and its subsidiaries and may be
 * used for internal evaluation purposes or commercial use strictly subject to separate
 * license agreement between you and TomTom NV. If you are the licensee, you are only permitted
 * to use this software in accordance with the terms of your license agreement. If you are
 * not the licensee, you are not authorized to use this software in any manner and should
 * immediately return or destroy it.
 */

#pragma once

#include <orodoro/utils/polyline.hpp>

#include <tomtom/sdk/routing/route/route_data.hpp>

#include <string>

namespace tomtom {
namespace navkit2 {
namespace tripservice {
namespace polylinedumphelpers {

template <class Stream>
void PolylineToStreamAsGMapJS(Stream& out,
                              const std::string& js_array_name,
                              const orodoro::Polyline& src)
{
    out << "const " << js_array_name << " = [";
    std::for_each(src.begin(), src.end(), [&out](const auto& point) {
        out << std::fixed << std::setprecision(8) << "{ lat: " << point.LatitudeInDegrees()
            << ", lng: " << point.LongitudeInDegrees() << "},";
    });
    out << "];";
}

template <class Stream>
void PolylineToStreamAsGMapJS(Stream& out, const std::string& js_array_name, const RouteData& src)
{
    const static orodoro::Polyline empty;
    PolylineToStreamAsGMapJS(out, js_array_name, (src.polyline_) ? *src.polyline_ : empty);
}

template <class Stream>
void SegmentsToStreamAsGMapJS(Stream& out,
                              const std::string& js_array_name,
                              const Segments& segments)
{
    out << "const " << js_array_name << " = [";
    for (const auto& segment : segments)
    {
        out << "{start_point_index: " << segment.start_point_index
            << ", end_point_index: " << segment.end_point_index << "}, ";
    }
    out << "];";
}

template <class Stream>
void SegmentsToStreamAsGMapJS(Stream& out, const std::string& js_array_name, const RouteData& src)
{
    SegmentsToStreamAsGMapJS(out, js_array_name, src.segments_);
}

}  // namespace polylinedumphelpers
}  // namespace tripservice
}  // namespace navkit2
}  // namespace tomtom


/*

Use example:

#ifdef UNCOMMENT_THIS_TO_DUMP_POLYS_AS_JS_FOR_GOOGLE_MAPS
    using namespace polylinedumphelpers;
    std::stringstream stream_polylines;
    PolylineToStreamAsGMapJS(stream_polylines, "sourcePolyline", route_data);
    PolylineToStreamAsGMapJS(stream_polylines, "targetPolyline", resolved_route_data);
#endif



#ifdef UNCOMMENT_THIS_TO_DUMP_POLYS_AS_JS_FOR_GOOGLE_MAPS
    PolylineToStreamAsGMapJS(stream_polylines, "combinedPolyline", resolved_route_data);
    SegmentsToStreamAsGMapJS(stream_polylines, "sourceSegments", route_data);
    SegmentsToStreamAsGMapJS(stream_polylines, "targetSegments", resolved_route_data);

    stream_polylines << "const indexMapping = [";
    for (size_t i = 0, sz = index_mapping.size(); i < sz; ++i)
    {
        stream_polylines << "{ isrc: " << i << ", itgt: " << index_mapping[i] << "},";
    }
    stream_polylines << "];";

    std::cout.flush();
    std::cerr.flush();

    ODO_LOG_ERROR(kDumpLogMarker, "{}", stream_polylines.str());
    if (route_data.polyline_->size() > 100)
    {
        const std::string home(std::getenv("HOME"));
        std::fstream out(home + "/polyline_dump_latest_call.txt",
                         std::ios_base::trunc | std::fstream::out);
        out << stream_polylines.str() << std::endl;
    }
#endif

*/
