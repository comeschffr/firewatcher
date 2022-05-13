import configparser
import logging
import os
import sys

import matplotlib.pyplot as plt

from collect_data import CollectedData
from final_report import FinalReport


config = configparser.ConfigParser()
config.read("config.ini")
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(config['DEFAULT']['logfile']),
        logging.StreamHandler()
    ]
)
plt.set_loglevel("WARNING")


def get_float_from_user(msg):
    while True:
        val = input(msg)
        try:
            val = float(val)
        except ValueError:
            if val.lower() == 'quit':
                print("Goodbye!")
                sys.exit()
            print("Wrong input... please try again")
            continue
        else:
            break
    return val


if __name__=="__main__":
    # lat, lon = 45.5, 9.2 # perform tests on user input
    # lat, lon = 41.85, -87.65 # perform tests on user input

    with open('welcome_banner.txt', encoding='utf8') as f:
        contents = f.read()
        print(
            contents
            .replace("\*/", u'\U0001f6a8\U0001f6a8')
            .replace("\**/", u'\U0001f692\U0001f9ef\U0001f525')
        )

    while True:
        lat = get_float_from_user(">>> LAT: ")
        lat = get_float_from_user(">>> LON: ")

        lat, lon = 38.219693, -94.259806 # perform tests on user input

        data = CollectedData(lat=lat, lon=lon, weather_api_key=config['DEFAULT']['api_key'])
        data.imgs[0].run_color_analysis()
        data.imgs[1].run_color_analysis()

        data.compute_risk()

        path = data.weather_data.make_temperature_chart()
        path = data.weather_data.make_humidity_rain_chart()
        path = data.weather_data.make_wind_chart()
        path = data.weather_data.make_sunlight_chart()

    final_report_path = "fp.pdf"
    final_report = FinalReport(final_report_path)
    logging.info('Report was saved successfully at ' + os.getcwd() + "\\" + final_report_path)
