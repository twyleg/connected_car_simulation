import gpxpy
from gpxpy.gpx import GPXTrackPoint


class Route:

    def __init__(self, gpx_file_path: str):
        gpx_file = open(gpx_file_path, 'r')
        self.gpx = gpxpy.parse(gpx_file)

        self.waypoints = self.calculate_waypoints();

    def calculate_waypoints(self) -> list[GPXTrackPoint]:
        points = self.gpx.tracks[0].segments[0].points
        overall_dist = 0
        interpol_dist = 0.0

        waypoints: list[GPXTrackPoint] = []

        for i in range(0, len(points)-1):
            current_point = points[i]
            next_point = points[i+1]

            dist = current_point.distance_2d(next_point)
            overall_dist = overall_dist + dist

            if dist > 0.0:
                delta_lat = next_point.latitude - current_point.latitude
                delta_lon = next_point.longitude - current_point.longitude

                delta_lat_norm = delta_lat / dist
                delta_lon_norm = delta_lon / dist

                while interpol_dist < dist:
                    interpol_lat = current_point.latitude + delta_lat_norm * interpol_dist
                    interpol_lon = current_point.longitude + delta_lon_norm * interpol_dist
                    # self.waypoints.append({"lon": interpol_lon, "lat": interpol_lat})
                    waypoints.append(GPXTrackPoint(latitude=interpol_lat, longitude=interpol_lon))
                    interpol_dist = interpol_dist + 1.0

                interpol_dist = dist % 1.0

        return waypoints

    def interpolate_track_point(self, first_trackpoint: GPXTrackPoint, second_trackpoint: GPXTrackPoint,
                                interpol_dist: float) -> GPXTrackPoint:
        dist_between_trackpoints = first_trackpoint.distance_2d(second_trackpoint)

        delta_lat = second_trackpoint.latitude - first_trackpoint.latitude
        delta_lon = second_trackpoint.longitude - first_trackpoint.longitude

        interpol_lat = first_trackpoint.latitude + delta_lat * (interpol_dist / dist_between_trackpoints)
        interpol_lon = first_trackpoint.longitude + delta_lon * (interpol_dist / dist_between_trackpoints)

        return GPXTrackPoint(latitude=interpol_lat, longitude=interpol_lon)

    def get_track_point_by_dist(self, dist: float) -> GPXTrackPoint:
        first_trackpoint = self.waypoints[int(dist)]
        second_trackpoint = self.waypoints[int(dist)+1]
        return self.interpolate_track_point(first_trackpoint, second_trackpoint, dist % 1.0)
