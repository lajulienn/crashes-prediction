import xarray as xr
import pickle
import pytz
import warnings
import importlib.util
from astral import Location
from workalendar.europe import Russia

from . import config

# import module from code
spec = importlib.util.spec_from_file_location("getncepreanalisys",
                                              config.WEATHER_PATH + '/getncepreanalisys.py')
getncepreanalisys = importlib.util.module_from_spec(spec)
spec.loader.exec_module(getncepreanalisys)


class FeatureConstructor:
    def __init__(self):
        self.__features = None
        self.__etopo = xr.open_dataset(config.ETOPO_DS_PATH)
        self.__precipitation_ds = xr.merge(
            map(lambda y: xr.open_dataset(config.PRECIPITATION_DS_PATH % y),
                config.YEARS
            )
        )
        self.__timezone = pytz.timezone('Europe/Moscow')
        # with open(config.WEATHER_PATH + "/w-12-19.pkl", 'rb') as file:
        #     self.__weather_ds = pickle.load(file)

    def __set_year(self):
        self.__features['year'] = self.__features.get('datetime').year

    def __set_hour(self):
        hour = self.__features.get('datetime').hour
        minute = self.__features.get('datetime').minute
        self.__features['hour'] = (hour + minute // 30) % 24

    def __set_elevation(self):
        elevation = self.__etopo.sel(
            x=self.__features.get('longitude'),
            y=self.__features.get('latitude'),
            method='nearest'
        ).z.values.item(0)
        self.__features['elevation'] = elevation

    def __set_sunlight_info(self):
        location = Location((
            None,
            None,
            self.__features.get('latitude'),
            self.__features.get('longitude'),
            'Europe/Moscow',
            self.__features.get('elevation'),
        ))

        date_time = self.__features.get('datetime')
        sun = location.sun(date_time)

        self.__features['when'] = 'twilight'
        if sun['sunrise'] < date_time < sun['sunset']:
            self.__features['when'] = 'day'
        elif date_time < sun['dawn'] or date_time > sun['dusk']:
            self.__features['when'] = 'night'

        self.__features['solar_azimuth'] = location.solar_azimuth(date_time)
        self.__features['solar_elevation'] = location.solar_elevation(date_time)
        self.__features['solar_zenith'] = location.solar_zenith(date_time)

    def __set_calendar_info(self):
        date_time = self.__features.get('datetime')

        self.__features['isworkingday'] =  Russia().is_working_day(date_time)
        self.__features['dayofweek'] = date_time.strftime("%A")
        self.__features['month'] = date_time.strftime("%B")

    def __set_precipitation(self):
        self.__precipitation_ds.sel(
            lon=self.__features.get('longitude'),
            lat=self.__features.get('latitude'),
            time=self.__features.get('datetime'),
            method='nearest'
        ).precip.values.item(0)

    def __set_weather_data(self):
        attrs = ['t1w', 't2w', 't3w', 'h1w', 'h2w', 'h3w',
                 'temperature', 'uwind', 'vwind', 'humidity']
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            point = getncepreanalisys.point_time_weather(
                self.__weather_ds,
                self.__features.get('longitude'),
                self.__features.get('longitude'),
                self.__features.get('datetime').date()
            )
            for attr in attrs:
                self.__features[attr] = point[attr]

        attrs = ['10m_u_component_of_wind', '10m_v_component_of_wind', '2m_dewpoint_temperature',
                 '2m_temperature', 'evaporation_from_bare_soil',
                 'evaporation_from_open_water_surfaces_excluding_oceans',
                 'runoff', 'snow_cover', 'snow_depth',
                 'snowfall', 'snowmelt',
                 'soil_temperature_level_1', 'surface_pressure', 'surface_runoff',
                 'total_precipitation', 'volumetric_soil_water_layer_1']

        datasets = {}
        for attr in attrs:
            year = self.__features.get('datetime').year
            try:
                ds = datasets['%s_%d' % (attr, year)]
            except:
                datasets['%s_%d' % (attr, year)] = xr.open_dataset(
                    './weather/%s_%d.grib' % (attr, year),
                    engine='cfgrib'
                )
                ds = datasets['%s_%d' % (attr, year)]
            try:
                value = ds.sel(
                    longitude=self.__features.get('longitude'),
                    latitude=self.__features.get('latitude'),
                    time=self.__features.get('datetime').date(),
                    step=self.__features.get('datetime') - self.__features.get('datetime').normalize(),
                    method='nearest'
                )
            except:
                value = ds.sel(
                    longitude=self.__features.get('longitude'),
                    latitude=self.__features.get('latitude'),
                    time=self.__features.get('datetime'),
                    method='nearest'
                )
            self.__features[attr] = value[list(ds.data_vars.keys())[0]].values.item(0)

    def __set_terrain_data(self):
        attrs = [
            'slope_riserun',
            'slope_percentage',
            'slope_degrees',
            'slope_radians',
            'aspect',
            'curvature',
            'planform_curvature',
            'profile_curvature'
        ]

        for attr in attrs:
            ds = xr.open_rasterio(config.CRASHES_PATH + '/%s.tiff' % attr)
            self.__features[attr] = ds.sel(
                x=self.__features.get('longitude'),
                y=self.__features.get('latitude'),
                band=1,
                method='nearest'
            ).values.item(0)

    def get_feature_dataframe(self, latitude, longitude, date_time):
        self.__features = {
            'latitude': latitude,
            'longitude': longitude,
            'datetime': date_time.astimezone(self.__timezone),
        }

        self.__set_year()
        self.__set_hour()
        self.__set_elevation()
        self.__set_sunlight_info()
        self.__set_calendar_info()
        self.__set_precipitation()
        # self.__set_weather_data()
        self.__set_terrain_data()

        return self.__features
