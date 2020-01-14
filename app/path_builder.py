import json

import requests
from geopy.exc import GeopyError
from geopy.geocoders import Nominatim

from . import config


class GeocodeError(Exception):
    pass


class Geocode:
    def __init__(self, location: str):
        self.location_description = location

    def nominatim_(self) -> list:
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

    def yandex_(self) -> list:
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
        coordinates = self.nominatim_()
        if not coordinates:
            coordinates = self.yandex_()
        return coordinates


def get_coordinates_by_description(location_description: str) -> list:
    coordinates = Geocode(location_description).get_coordinates()
    if not coordinates:
        raise GeocodeError

    return coordinates


def get_path_points_between_coordinates(source: list,
                                        destination: list,
                                        number_of_points: int) -> list:
    return []
