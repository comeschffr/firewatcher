import logging
import math
import uuid
from datetime import datetime

import ee
import matplotlib.pyplot as plt
import requests
from requests.adapters import HTTPAdapter, Retry
from tqdm import tqdm

from image_analysis import SatelliteImage


class CollectedData():
    def __init__(self, lat: float, lon: float, weather_api_key: str, resources_folder: str) -> None:
        # in case the user wants to generate several reports, initializing GEE can be skipped
        if not getattr(self, 'established', False):
            self.initialize_gee()
        self.lat = lat
        self.lon = lon
        self._resources_folder = resources_folder
        self.indicators = {}
        self.make_aoi()
        self.get_most_recent_imgs()
        self.get_imgs_download_url()
        self.download_files()

        self.imgs = []
        for i, (arr_filename, gee_img_date) in enumerate(zip(self.arrs_filename, self.gee_imgs_date)):
            new_img = SatelliteImage(
                arr_filename,
                gee_img_date,
                i+1,
                self._resources_folder
            )
            self.imgs.append(new_img)

        self.weather_data = WeatherData(self.lat, self.lon, weather_api_key, self._resources_folder)

    def __repr__(self) -> str:
        rep = self.__dict__.copy()
        rep['aoi'] = "ee.Geometry.Polygon("+str(self.aoi.getInfo())+")"
        rep['collection'] = "ee.ImageCollection(id="+self.collection.getInfo()['id']+")"
        return (
            f"CollectedData({', '.join([key+'='+str(val) for key, val in rep.items()])})"
        )

    def initialize_gee(self) -> None:
        # ee.Authenticate()
        logging.info("Initializing Google Earth Engine...")
        ee.Initialize()
        logging.info("Google Earth Engine initialized successfully!")
        self.established = True

    def make_aoi(self) -> ee.Geometry.Polygon:
        """
        Making the Area of Interest object to use the GEE library
        """
        self.aoi = ee.Geometry.Polygon(
            [[
                [self.lon-0.1, self.lat+0.1],
                [self.lon-0.1, self.lat-0.1],
                [self.lon+0.1, self.lat-0.1],
                [self.lon+0.1, self.lat-0.1],
            ]],
            None,
            False
        )
        return self.aoi

    def get_gee_img_date(self, gee_img: ee.Image) -> datetime:
        timestamp = gee_img.getInfo()['properties']['system:time_start']
        return datetime.fromtimestamp(timestamp/1000)

    def __remove_duplicate_dates(self, list_of_imgs: ee.List) -> ee.List:
        """
        Removing images that have the same date
        This case happends when the AoI lies between two tiles
        """
        already_seen_dates = set()
        cleaned_img_list = ee.List([])

        for i in range(list_of_imgs.size().getInfo()):
            date_acquired = list_of_imgs.get(i).getInfo()['properties']['DATE_ACQUIRED']
            if date_acquired not in already_seen_dates:
                cleaned_img_list = cleaned_img_list.add(list_of_imgs.get(i))
                already_seen_dates.add(date_acquired)

        return cleaned_img_list

    def get_most_recent_imgs(self) -> list[ee.Image, ee.Image]:
        """
        Query GEE library to get the 2 most recend and clearest images
        A dataset-specific scale factor is also applied
        """
        self.collection = (
            ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
            .filterBounds(self.aoi)
            .filter("CLOUD_COVER < 55")
            .sort('CLOUD_COVER')
            .sort('system:time_start', False)
        )

        def applyScaleFactors(image):
            opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
            thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0);
            return image.addBands(opticalBands, None, True).addBands(thermalBands, None, True);

        self.collection = self.collection.map(applyScaleFactors)

        list_of_imgs = self.collection.toList(self.collection.size().getInfo())
        list_of_imgs = self.__remove_duplicate_dates(list_of_imgs)

        if list_of_imgs.size().getInfo() < 2:
            raise ValueError("Could not find enough images for further analysis (<2 images)")

        self.gee_imgs = [
            ee.Image(list_of_imgs.get(0)).select("SR_B4", "SR_B3", "SR_B2"),
            ee.Image(list_of_imgs.get(1)).select("SR_B4", "SR_B3", "SR_B2"),
        ]
        self.gee_imgs_date = [
            self.get_gee_img_date(self.gee_imgs[0]),
            self.get_gee_img_date(self.gee_imgs[1]),
        ]

        return self.gee_imgs

    def get_imgs_download_url(self) -> list[str, str]:
        self.imgs_url = []
        for sat_img in self.gee_imgs:
            self.imgs_url.append(
                sat_img.getDownloadURL(
                    {
                        'region': self.aoi,
                        'dimensions': "1000x1000", # 1365x1365 max resolution for authorized request size
                        'format': "npy",
                    }
                )
            )
            logging.info(f"Found URL successfully: {self.imgs_url[-1]}")

        return self.imgs_url

    def __gee_request_to_save(self, s: requests.sessions.Session, url: str, filename: str) -> None:
        try:
            r = s.get(url, stream=True, timeout=10)
        except requests.exceptions.ConnectionError:
            logging.error("Failed to download the image")
            return

        total = int(r.headers.get('content-length', 0))

        logging.info(f"Saving raw request content to {filename}")
        with open(filename, "wb") as f, tqdm(
            total=total,
            unit="iB",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in r.iter_content(chunk_size=1024):
                size = f.write(data)
                bar.update(size)

    def download_files(self) -> list[str, str]:
        """
        Downloading and saving the 2 images as numpy arrays
        """
        curr_date = datetime.now().strftime("%m-%d-%Y_%H%M%S")
        base_filename_uuid = str(uuid.uuid4())[:8]
        self.arrs_filename = [
            (
                self._resources_folder + "/" + base_filename_uuid + "_" +
                str(self.lat) + "_" + str(self.lon) + "_" +
                curr_date + "_" + "1" + ".arr"
            ),
            (
                self._resources_folder + "/" + base_filename_uuid + "_" +
                str(self.lat) + "_" + str(self.lon) + "_" +
                curr_date + "_" + "2" + ".arr"
            )
        ]

        s = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.1
        )
        s.mount('https://', HTTPAdapter(max_retries=retries))

        for img_url, img_filepath in zip(self.imgs_url, self.arrs_filename):
            logging.info(f"Requesting image at {img_url}...")
            self.__gee_request_to_save(s, img_url, img_filepath)

        return self.arrs_filename

    def _get_index(self, avg_metric, scale):
        for i, threshold in enumerate(scale):
            if avg_metric < threshold:
                return i
        return len(scale)

    def compute_risk(self) -> float:
        """
        Compute final risk index from all the data collected
        """
        self.indicators['dryness'] = []
        for color1, color2 in zip(self.imgs[0].p_and_c, self.imgs[1].p_and_c):
            r1, r2 = color1['rgb'][0].item(), color2['rgb'][0].item()
            g1, g2 = color1['rgb'][1].item(), color2['rgb'][1].item()
            _dryness = (1 + (r1 - r2) / r2) * (1 + (g2 - g1) / g1)
            self.indicators['dryness'].append(_dryness)

        _avg_wind = sum(self.weather_data.wind) / len(self.weather_data.wind)
        _beaufort_scale = [0.5, 1.5, 3.3, 5.5, 7.9, 10.7, 13.8, 17.1, 20.7, 24.4, 28.4, 32.6]
        self.indicators['wind'] = (self._get_index(_avg_wind, _beaufort_scale) + 1) / len(_beaufort_scale)

        self.indicators['humidity'] = sum(self.weather_data.humidity) / len(self.weather_data.humidity)
        self.indicators['humidity'] = 1 - self.indicators['humidity'] / 100

        _avg_rain = sum(self.weather_data.rain) / len(self.weather_data.rain)
        _rainfall_classification = [10, 35.5, 64.4, 124.4]
        self.indicators['rain'] = 1 - self._get_index(_avg_rain, _rainfall_classification) / len(_rainfall_classification)

        _avg_temp = sum(self.weather_data.temperature) / len(self.weather_data.temperature)
        _temp_classification = [4.1, 8.0, 13.0, 18.0, 23.0, 29.0, 35.0, 41.0]
        self.indicators['temp'] = (self._get_index(_avg_temp, _temp_classification) + 1) / len(_temp_classification)

        self.indicators['sunlight'] = sum(self.weather_data.sunlight) / len(self.weather_data.sunlight)
        self.indicators['sunlight'] /= 11

        logging.info(self.indicators)

        self.overall_risk = (
            math.prod(self.indicators['dryness'])
            * self.indicators['wind']
            * self.indicators['humidity']
            * self.indicators['rain']
            * self.indicators['temp']
            * self.indicators['sunlight']
        )
        logging.info("Final risk: " + str(self.overall_risk))

        return self.overall_risk


class WeatherData():
    def __init__(self, lat: float, lon: float, api_key: str, resources_folder: str) -> None:
        self.lat = lat
        self.lon = lon
        self.api_key = api_key
        self._resources_folder = resources_folder
        self.get_and_set_data_from_api()

    def __repr__(self) -> str:
        rep = self.__dict__.copy()
        rep['api_key'] = '*'*(len(rep['api_key'])-8) + rep['api_key'][-8:]
        return (
            f"WeatherData({', '.join([key+'='+str(val) for key, val in rep.items()])})"
        )

    def get_and_set_data_from_api(self) -> None:
        """
        Query the weather API and structure useful data
        """
        weather_url = "https://api.openweathermap.org/data/2.5/onecall"
        parameters = {
            'lat': self.lat,
            'lon': self.lon,
            'exclude': "current,minutely,hourly",
            'appid': self.api_key,
            'units': "metric"
        }
        r = requests.get(weather_url, params=parameters)
        req_data = r.json()

        self.dates = [datetime.fromtimestamp(day['dt']) for day in req_data['daily']]
        self.temperature = [day['temp']['day'] for day in req_data['daily']]
        self.humidity = [day['humidity'] for day in req_data['daily']]
        self.wind = [day['wind_speed'] for day in req_data['daily']]
        self.rain = [day.get('rain', 0) for day in req_data['daily']]
        self.rain_p = [day['pop'] for day in req_data['daily']]
        self.sunlight = [day['uvi'] for day in req_data['daily']]

    def make_temperature_chart(self) -> str:
        curr_date = datetime.now().strftime("%m-%d-%Y_%H%M%S")
        graph_filename = f"{self._resources_folder}/temperature_chart_{curr_date}.svg"
        day_labels = [dt.strftime("%m/%d") for dt in self.dates]

        plt.bar(day_labels, self.temperature, color="firebrick")
        plt.title("Temperature Forecast", fontsize=50)
        plt.ylabel("°C", fontsize='xx-large')
        plt.xticks(fontsize='xx-large')
        plt.yticks(fontsize='xx-large')
        plt.savefig(graph_filename)
        plt.clf()

        return graph_filename

    def make_humidity_rain_chart(self) -> str:
        curr_date = datetime.now().strftime("%m-%d-%Y_%H%M%S")
        graph_filename = f"{self._resources_folder}/hum_rain_chart_{curr_date}.svg"
        day_labels = [dt.strftime("%m/%d") for dt in self.dates]

        fig, ax = plt.subplots()
        bar1 = ax.bar(day_labels, self.rain, color="aqua", label="rain")
        ax.set_ylabel("Rain volume (in mm)")
        ax.legend(loc=0)
        ax2 = ax.twinx()
        line1 = ax2.plot(day_labels, self.humidity, marker='o', color="lightsteelblue", label="humidity")
        ax2.set_ylabel("Humidity (in %)")
        ax2.set_ylim(bottom=0, top=100)

        legends = [bar1, line1[0]]
        labs = [leg.get_label() for leg in legends]
        ax.legend(legends, labs, loc=0)

        plt.title("Rain and Humidity Forecast", fontsize=20)
        fig.savefig(graph_filename)
        plt.clf()

        return graph_filename

    def make_wind_chart(self) -> str:
        curr_date = datetime.now().strftime("%m-%d-%Y_%H%M%S")
        graph_filename = f"{self._resources_folder}/wind_chart_{curr_date}.svg"
        day_labels = [dt.strftime("%m/%d") for dt in self.dates]

        plt.plot(day_labels, self.wind, marker='o', color="olivedrab")
        plt.title("Wind forecast", fontsize=20)
        plt.ylabel("m/s")
        plt.savefig(graph_filename)
        plt.clf()

        return graph_filename

    def make_sunlight_chart(self) -> str:
        curr_date = datetime.now().strftime("%m-%d-%Y_%H%M%S")
        graph_filename = f"{self._resources_folder}/sunlight_chart_{curr_date}.svg"
        day_labels = [dt.strftime("%m/%d") for dt in self.dates]

        plt.bar(day_labels, self.sunlight, color="gold")
        plt.title("Sunlight forecast", fontsize=20)
        plt.ylabel("UV index")
        plt.ylim(top=10)
        plt.savefig(graph_filename)
        plt.clf()

        return graph_filename
