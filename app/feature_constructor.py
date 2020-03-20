import os
import pickle
from datetime import datetime
from timeit import default_timer as timer

import pytz
import xarray as xr
from astral import Location
from siphon.catalog import TDSCatalog
from workalendar.europe import Russia

import config


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
        with open(os.path.join(config.WEATHER_PATH, "/w-12-19.pkl"), 'rb') as file:
            self.__weather_ds = pickle.load(file)

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

        self.__features['isworkingday'] = Russia().is_working_day(date_time)
        self.__features['dayofweek'] = date_time.strftime("%A")
        self.__features['month'] = date_time.strftime("%B")

    def __set_weather_data(self):
        time = datetime.utcnow()  # self.__features.get('datetime')

        forecastvariables = [
            'Temperature_isobaric',
            'Relative_humidity_isobaric',
            'u-component_of_wind_isobaric',
            'v-component_of_wind_isobaric',
            'Soil_temperature_depth_below_surface_layer',
            'Pressure_surface',
            'Water_runoff_surface_Mixed_intervals_Accumulation',
            'Total_precipitation_surface_Mixed_intervals_Accumulation',
            'Volumetric_Soil_Moisture_Content_depth_below_surface_layer',
        ]
        gfs_cat = TDSCatalog(config.TDSCATALOG_URL)
        latest = gfs_cat.latest
        ncss = latest.subset()
        query = ncss.query().variables(*forecastvariables)
        query.time(time).accept('netCDF4')
        nc = ncss.get_data(query)
        fds = xr.open_dataset(xr.backends.NetCDF4DataStore(nc))
        fds = fds.sel(isobaric=100000)
        fds = fds.rename({
            'Relative_humidity_isobaric': 'humidity',
            'Temperature_isobaric': 'temperature',
            'u-component_of_wind_isobaric': 'uwind',
            'v-component_of_wind_isobaric': 'vwind',
            'Soil_temperature_depth_below_surface_layer': 'soil_temperature_level_1',
            'Pressure_surface': 'surface_pressure',
            'Water_runoff_surface_Mixed_intervals_Accumulation': 'surface_runoff',
            'Total_precipitation_surface_Mixed_intervals_Accumulation': 'total_precipitation',
            'Volumetric_Soil_Moisture_Content_depth_below_surface_layer': 'volumetric_soil_water_layer_1',
        })
        try:
            fds = fds.rename({'time3': 'time'})
        except:
            pass

        latitude = self.__features.get('latitude')
        longitude = self.__features.get('longitude')
        fm = fds.sel(lat=latitude, lon=longitude, time=time, method='nearest')

        self.__features['temperature'] = fm.temperature.values.item(0)
        self.__features['humidity'] = fm.humidity.values.item(0)
        self.__features['uwind'] = fm.uwind.values.item(0)
        self.__features['vwind'] = fm.vwind.values.item(0)
        self.__features['soil_temperature_level_1'] = fm.soil_temperature_level_1.values.item(0)
        self.__features['surface_pressure'] = fm.surface_pressure.values.item(0)
        self.__features['surface_runoff'] = fm.surface_runoff.values.item(0)
        self.__features['total_precipitation'] = fm.total_precipitation.values.item(0)
        self.__features['volumetric_soil_water_layer_1'] = fm.volumetric_soil_water_layer_1.values.item(0)

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

    def get_features_list(self, latitude, longitude, date_time):
        self.__features = {
            'latitude': latitude,
            'longitude': longitude,
            'datetime': date_time.astimezone(self.__timezone),
        }

        # start = timer()
        self.__set_year()
        # print(f'set_year(): {timer() - start}')

        # start = timer()
        self.__set_hour()
        # print(f'set_hour(): {timer() - start}')

        # start = timer()
        self.__set_elevation()
        # print(f'set_elevation(): {timer() - start}')

        # start = timer()
        self.__set_sunlight_info()
        # print(f'set_sunlight_info(): {timer() - start}')

        # start = timer()
        self.__set_calendar_info()
        # print(f'set_calendar_info(): {timer() - start}')

        # start = timer()
        # self.__set_weather_data()
        # print(f'set_weather_info(): {timer() - start}')

        # start = timer()
        self.__set_terrain_data()
        # print(f'set_terrain_info(): {timer() - start}')

        feature_list = [self.__features.get(feature) for feature in config.FEATURES]

        return feature_list
