import logging

import matplotlib.pyplot as plt

from collect_data import CollectedData


logging.basicConfig(level=logging.INFO)
plt.set_loglevel("WARNING")


if __name__=="__main__":
    # lat, lon = 45.5, 9.2 # perform tests on user input
    # lat, lon = 41.85, -87.65 # perform tests on user input
    lat, lon = 38.219693, -94.259806 # perform tests on user input

    data = CollectedData(lat=lat, lon=lon)
    data.imgs[0].run_color_analysis()
    data.imgs[1].run_color_analysis()

    path = data.weather_data.make_temperature_chart()
    path = data.weather_data.make_humidity_rain_chart()
    path = data.weather_data.make_wind_chart()
    path = data.weather_data.make_sunlight_chart()
