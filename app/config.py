# GEOCODE
YANDEX_API_KEY = '611c97ab-4f96-4575-b166-75878a497f8c'
NOMINATIM_USER_AGENT = 'datadigger'
NOMINATIM_DOMAIN = 'datadigger.ru:7070'
NOMINATIM_SCHEME = 'http'
GRAPHHOPPER_KEY = 'ba54db28-5e83-424a-a5af-f2c3b58369bf'

# MODEL
MODEL_FILENAME = '/data/crashes/small_model_no_weather_dump'
DUMP_FORMAT = 'cbm'
YEARS = [2015, 2016, 2017, 2018]
FEATURES = [
    'isworkingday',
    'elevation',
    'solar_azimuth',
    'solar_elevation',
    'solar_zenith',
    # 'temperature',
    # 'uwind',
    # 'vwind',
    # 'humidity',
    'slope_riserun',
    'slope_percentage',
    'slope_degrees',
    'slope_radians',
    'aspect',
    'curvature',
    'planform_curvature',
    'profile_curvature',
    # 'soil_temperature_level_1',
    # 'surface_pressure',
    # 'surface_runoff',
    # 'total_precipitation',
    # 'volumetric_soil_water_layer_1',
]

# SERVER PATHS
ETOPO_DS_PATH = '/data/elevation/ETOPO1_Bed_g_gmt4.grd'
PRECIPITATION_DS_PATH = '/data/weather/datasets/precip.%d.nc'
WEATHER_PATH = '/data/weather'
CRASHES_PATH = '/data/crashes'

# OTHER
TDSCATALOG_URL = 'http://thredds.ucar.edu/thredds/catalog/grib/NCEP/GFS/Global_0p5deg/catalog.xml'
