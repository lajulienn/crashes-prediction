import json

import requests
from geopy.exc import GeopyError
from geopy.geocoders import Nominatim

import config


class GeocodeError(Exception):
    pass

class PathBuildError(Exception):
    pass


class Geocode:
    def __init__(self, location: str):
        self.location_description = location

    def __nominatim(self) -> list:
        try:
            nominatim = Nominatim(
                user_agent=config.NOMINATIM_USER_AGENT,
                domain=config.NOMINATIM_DOMAIN,
                scheme=config.NOMINATIM_SCHEME,
            )
            location = nominatim.geocode(self.location_description)
        except GeopyError:
            location = None

        if location:
            location = [location.latitude, location.longitude]

        return location

    def __yandex(self) -> list:
        try:
            url = f'http://geocode-maps.yandex.ru/1.x/?apikey={config.YANDEX_API_KEY}' \
                  f'&geocode={self.location_description}&results=1&format=json'
            response = requests.get(url)
            response = json.loads(response.text)
            location = response.get('response').get('GeoObjectCollection').get('featureMember')[0] \
                .get('GeoObject').get('Point').get('pos')

            location = location.split()
            location = list([float(x) for x in location])
            location.reverse()
        except:
            location = None

        return location

    def get_coordinates(self):
        coordinates = self.__nominatim()
        if not coordinates:
            coordinates = self.__yandex()
        return coordinates


def get_coordinates_by_description(location_description: str) -> list:
    coordinates = Geocode(location_description).get_coordinates()
    if not coordinates:
        raise GeocodeError

    return coordinates


def get_path_points_between_coordinates(origin: list, destination: list) -> list:
    if len(origin) != 2 or len(destination) != 2:
        raise PathBuildError('Source and destination should be lists of length 2')

    url = f'https://graphhopper.com/api/1/route?point={origin[0]},{origin[1]}&' \
          f'point={destination[0]},{destination[1]}&vehicle=car&debug=true&' \
          f'key={config.GRAPHHOPPER_KEY}&type=json&points_encoded=False&' \
          f'instructions=False&alternative_route.max_paths=0'
    response = requests.get(url)
    response = json.loads(response.text)
    points = response.get('paths')[0].get('points').get('coordinates')
    points = [point[::-1] for point in points]

    return points
