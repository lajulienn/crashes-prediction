import xarray as xr
import pickle
import warnings
import importlib.util
from astral import Astral, Location
from workalendar.europe import Russia

from . import config

spec = importlib.util.spec_from_file_location("getncepreanalisys", config.WEATHER_PATH)
getncepreanalisys = importlib.util.module_from_spec(spec)
spec.loader.exec_module(getncepreanalisys)

class FeatureConstructor:
    def __init__(self):
        self.features = None
        self.etopo = xr.open_dataset(config.ETOPO_DS_PATH)
        self.precipitation_ds = xr.merge(
            map(lambda y: xr.open_dataset(config.PRECIPITATION_DS_PATH % y),
                config.YEARS
            )
        )
        with open("../weather/w-12-19.pkl", 'rb') as file:
            self.weather_ds = pickle.load(file)

    def set_year_(self):
        self.features['year'] = self.features.get('datetime').year

    def set_hour_(self):
        hour = self.features.get('datetime').hour
        minute = self.features.get('datetime').minute
        self.features['hour'] = (hour + minute // 30) % 24

    def set_elevation_(self):
        self.features['elevation'] = self.etopo.sel(
            x=self.features.get('longitude'),
            y=self.features.get('latitude'),
            method='nearest'
        ).z.values.item(0)

    def set_sunlight_info_(self):
        location = Location((
            None,
            None,
            self.features.get('latitude'),
            self.features.get('longitude'),
            'Europe/Moscow',
            self.features.get('elevation'),
        ))

        date_time = self.features.get('datetime')
        sun = location.sun(date_time)

        self.features['when'] = 'twilight'
        if sun['sunrise'] < date_time < sun['sunset']:
            self.features['when'] = 'day'
        elif date_time < sun['dawn'] or date_time > sun['dusk']:
            self.features['when'] = 'night'

        self.features['solar_azimuth'] = location.solar_azimuth(date_time)
        self.features['solar_elevation'] = location.solar_elevation(date_time)
        self.features['solar_zenith'] = location.solar_zenith(date_time)

    def set_calendar_info_(self):
        date_time = self.features.get('datetime')

        self.features['isworkingday'] =  Russia().is_working_day(date_time)
        self.features['dayofweek'] = date_time.strftime("%A")
        self.features['month'] = date_time.strftime("%B")

    def set_precipitation_(self):
        self.precipitation_ds.sel(
            lon=self.features.get('longitude'),
            lat=self.features.get('latitude'),
            time=self.features.get('datetime'),
            method='nearest'
        ).precip.values.item(0)

    def set_weather_data_(self):
        attrs = ['t1w', 't2w', 't3w', 'h1w', 'h2w', 'h3w',
                 'temperature', 'uwind', 'vwind', 'humidity']
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            point = getncepreanalisys.point_time_weather(
                self.weather_ds,
                self.features.get('longitude'),
                self.features.get('longitude'),
                self.features.get('datetime').date()
            )
            for attr in attrs:
                self.features[attr] = point[attr]

        attrs = ['10m_u_component_of_wind', '10m_v_component_of_wind', '2m_dewpoint_temperature',
                 '2m_temperature', 'evaporation_from_bare_soil',
                 'evaporation_from_open_water_surfaces_excluding_oceans',
                 'runoff', 'snow_cover', 'snow_depth',
                 'snowfall', 'snowmelt',
                 'soil_temperature_level_1', 'surface_pressure', 'surface_runoff',
                 'total_precipitation', 'volumetric_soil_water_layer_1']

        datasets = {}
        for attr in attrs:
            year = self.features.get('datetime').year
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
                    longitude=self.features.get('longitude'),
                    latitude=self.features.get('latitude'),
                    time=self.features.get('datetime').date(),
                    step=self.features.get('datetime') - self.features.get('datetime').normalize(),
                    method='nearest'
                )
            except:
                value = ds.sel(
                    longitude=self.features.get('longitude'),
                    latitude=self.features.get('latitude'),
                    time=self.features.get('datetime'),
                    method='nearest'
                )
            self.features[attr] = value[list(ds.data_vars.keys())[0]].values.item(0)

    def set_terrain_data_(self):
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
            ds = xr.open_rasterio('%s.tiff' % attr)
            self.features[attr] = ds.sel(
                x=self.features.get('longitude'),
                y=self.features.get('latitude'),
                band=1,
                method='nearest'
            ).values.item(0)

    def get_feature_dataframe(self, latitude, longitude, date_time):
        self.features = {
            'latitude': latitude,
            'longitude': longitude,
            'datetime': date_time,
        }

        self.set_year_()
        self.set_hour_()
        self.set_elevation_()
        self.set_sunlight_info_()
        self.set_calendar_info_()
        self.set_precipitation_()
        self.set_weather_data_()
        self.set_terrain_data_()

        return self.features
