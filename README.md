# Предсказание вероятности аварий на маршруте

Сервис позволяет построить автомобильный маршрут между заданными точками
с указанием времени начала движения и оценить риски на полученном 
маршруте.

### Демо-версия

http://datadigger.ru:6060/predict_form

### Описание

Сервис получает на вход координаты начала и конца маршрута, 
а также время и дату поездки. С помощью API graphhopper.com
строится маршрут в виде списка точек. Затем для каждой 
точки составляется список фичей, используемых при предсказании:

```json
[
    "isworkingday",
    "elevation",
    "solar_azimuth",
    "solar_elevation",
    "solar_zenith",
    "slope_riserun",
    "slope_percentage",
    "slope_degrees",
    "slope_radians",
    "aspect",
    "curvature",
    "planform_curvature",
    "profile_curvature",
]
```

Фичи `"elevation", "aspect", "curvature", "planform_curvature", "profile_curvature"` рассчитываются на основе цифровой модели рельефа [ETOPO1](https://www.ngdc.noaa.gov/mgg/global) с разрешением в 1 угловую минуту на пиксел.

![curvature](https://richdem.readthedocs.io/en/latest/_images/ta_standard_curvature.png)

Для каждой точки вызывается predict_proba() заранее обученной модели 
классификации `CatBoostClassifier`, которая выдает вероятность аварии 
в заданное время.

### Качество модели

Accuracy: `0.87`

ROC AUC: `0.90` 
