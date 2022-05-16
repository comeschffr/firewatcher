import configparser
import logging
import sys
import webbrowser

from datetime import datetime

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
plt.set_loglevel(config['DEFAULT'].get('plt_loglevel', "WARNING"))


def get_float_from_user(msg, key):
    while True:
        val = input(msg)
        try:
            val = float(val)
            if key == "lat":
                if val < -90 or val > 90:
                    print("Latitude ranges from -90 to 90")
                    raise ValueError
            elif key == "lon":
                if val < -180 or val > 180:
                    print("Longitude ranges from -180 to 180")
                    raise ValueError
        except ValueError:
            if not val:
                return 38.219693 if key == "lat" else -94.259806
            if isinstance(val, str) and val.lower() == "quit":
                print("Goodbye!")
                sys.exit()
            print("Wrong input... please try again")
            continue
        else:
            break
    return val


if __name__ == "__main__":
    with open(config['DEFAULT']['welcome_banner'], encoding='utf8') as f:
        contents = f.read()
        print(
            contents
            .replace("\*/", u'\U0001f6a8\U0001f6a8') # replace methods to print emojis
            .replace("\**/", u'\U0001f692\U0001f9ef\U0001f525')
        )

    lat = get_float_from_user(">>> LAT: ", "lat")
    lon = get_float_from_user(">>> LON: ", "lon")
    # lat, lon = 38.219693, -94.259806 # for testing purpose only

    start = datetime.now()

    data = CollectedData(
        lat=lat,
        lon=lon,
        weather_api_key=config['DEFAULT']['api_key'],
        resources_folder=config['DEFAULT']['resources_folder'],
    )
    data.imgs[0].run_color_analysis()
    data.imgs[1].run_color_analysis()

    data.compute_risk()

    fp_resources = {
        'sat_img_1': data.imgs[0].rgb_img_filename,
        'sat_img_2': data.imgs[1].rgb_img_filename,
        'sat_col_1': data.imgs[0].make_block_graph(),
        'sat_col_2': data.imgs[1].make_block_graph(),
        'temp_chart': data.weather_data.make_temperature_chart(),
        'rain_chart': data.weather_data.make_humidity_rain_chart(),
        'wind_chart': data.weather_data.make_wind_chart(),
        'sunlight_chart': data.weather_data.make_sunlight_chart(),
    }
    logging.info(fp_resources)

    final_report = FinalReport(
        config['DEFAULT']['template_file'],
        {
            'lat': data.lat,
            'lon': data.lon,
            'date_image_1': data.gee_imgs_date[0].strftime("%Y-%m-%d %H:%M"),
            'date_image_2': data.gee_imgs_date[1].strftime("%Y-%m-%d %H:%M"),
        },
        data.overall_risk,
    )
    final_report.add_resources(fp_resources)
    final_report.generate()
    final_report.save()

    end = datetime.now()
    time_diff = round((end - start).total_seconds(), 2)
    logging.info(f"Report was generated in {time_diff} seconds")

    logging.info("Report was saved at " + final_report.file_name)

    print("Opening the report in your browser...")
    webbrowser.open(final_report.file_name, new=2) # new=2 to open in a new tab
