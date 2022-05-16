import logging
import uuid
from datetime import datetime
from time import time
from typing import Tuple

import cv2
import ee
import matplotlib.pyplot as plt
import numpy as np
import requests
from PIL import Image
from requests.adapters import HTTPAdapter, Retry
from sklearn.cluster import KMeans
from tqdm import tqdm


logging.basicConfig(level=logging.INFO)


class CollectedData():
    def __init__(self, lat: float, lon: float):
        # if not getattr(self, 'established', False):
        #     self.initialize_gee()
        self.lat = lat
        self.lon = lon
        # self.make_aoi()
        # self.get_most_recent_imgs()
        # self.get_imgs_download_url()
        # self.download_files()
        self.arrs_filename = [
            "images/76e9e3ba_38.219693_-94.259806_05-03-2022_181759_1.arr",
            "images/76e9e3ba_38.219693_-94.259806_05-03-2022_181812_2.arr",
        ]
        self.gee_imgs_date = [
            datetime(2022, 4, 19, 18, 54),
            datetime(2022, 3, 2, 17, 54),
        ]
        self.imgs = []
        # for arr_filename, gee_img_date in zip(self.arrs_filename, self.gee_imgs_date):
        #     new_img = SatelliteImage(
        #         arr_filename, 
        #         gee_img_date,
        #     )
        #     self.imgs.append(new_img)

        self.weather_data = WeatherData(self.lat, self.lon)

    def initialize_gee(self) -> None:
        # ee.Authenticate()
        logging.info("Initializing Google Earth Engine...")
        ee.Initialize()
        logging.info("Google Earth Engine initialized successfully!")
        self.established = True

    def make_aoi(self) -> ee.Geometry.Polygon:
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
        already_seen_dates = set()
        cleaned_img_list = ee.List([])

        for i in range(list_of_imgs.size().getInfo()):
            date_acquired = list_of_imgs.get(i).getInfo()['properties']['DATE_ACQUIRED']
            if date_acquired not in already_seen_dates:
                cleaned_img_list = cleaned_img_list.add(list_of_imgs.get(i))
                already_seen_dates.add(date_acquired)

        return cleaned_img_list

    def get_most_recent_imgs(self) -> list[ee.Image, ee.Image]:
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

        return

    def download_files(self) -> list[str, str]:
        curr_date = datetime.now().strftime("%m-%d-%Y_%H%M%S")
        base_filename_uuid = str(uuid.uuid4())[:8]
        self.arrs_filename = [
            (
                "images/" + base_filename_uuid + "_" +
                str(self.lat) + "_" + str(self.lon) + "_" +
                curr_date + "_" + "1" + ".arr"
            ),
            (
                "images/" + base_filename_uuid + "_" +
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


class SatelliteImage():
    def __init__(self, np_arr_filename: str, date: datetime):
        self.NB_CLUSTERS = 3
        self.date = date
        self.np_arr_filename = np_arr_filename
        self.np_arr = self.__to_np_arr()
        self.rgb_img = self.__to_rgb_img()
        self.rgb_img_filename = self.np_arr_filename.replace("arr", "png")
        self.rgb_save()

    def __to_np_arr(self) -> np.ndarray:
        logging.info("Creating numpy array from bytes response...")
        with open(self.np_arr_filename, "rb") as f:
            arr = np.lib.format.read_array(f)
        arr = np.array(arr.tolist())

        arr[arr < 0] = 0
        arr[arr > 0.3] = 0.3
        arr = (255 * (arr / 0.3)).astype('uint8')

        return arr

    def __to_rgb_img(self) -> Image:
        img = Image.fromarray(self.np_arr, 'RGB')
        return img
    
    def rgb_save(self) -> None:
        self.rgb_img.save(self.rgb_img_filename)

    def run_color_analysis(self) -> None:
        self.prepare()
        self.p_and_c_analysis()
        self.make_block_graph()
        self.make_bar_chart()
        self.make_final_output()

    def prepare(self) -> np.ndarray:
        tmp_arr = self.np_arr.copy()
        logging.info(f"Original image shape: {tmp_arr.shape}")

        tmp_arr = cv2.resize(tmp_arr, (200, 200), interpolation=cv2.INTER_AREA)
        logging.info(f"After resizing image: {tmp_arr.shape}")

        self.flat_arr = np.reshape(tmp_arr, (-1, 3))
        logging.info(f"After Flattening array: {self.flat_arr.shape}")

        return self.flat_arr

    def p_and_c_analysis(self) -> DominantColorsType:
        kmeans = KMeans(n_clusters=self.NB_CLUSTERS, random_state=0)
        kmeans.fit(self.flat_arr)

        percentages = np.unique(kmeans.labels_, return_counts = True)[1] / self.flat_arr.shape[0]
        dominant_colors = np.array(kmeans.cluster_centers_, dtype="uint")

        self.p_and_c = [
            {
                'percent': percent,
                'rgb': rgb,
            } for percent, rgb in sorted(zip(percentages, dominant_colors), reverse=True)
        ]

        return self.p_and_c

    def make_block_graph(self) -> str:
        file_name_box = "resources/dominant_colors_p2.png"

        block = np.ones((50, 50, self.NB_CLUSTERS), dtype="uint")

        for i, color in enumerate(self.p_and_c):
            block[:] = color['rgb']

            plt.subplot(1, self.NB_CLUSTERS, i+1)
            plt.imshow(block)
            plt.xticks([])
            plt.xlabel(
                str(round(color['percent']*100, 2)) + "%"
            )
            plt.yticks([])

        plt.savefig(file_name_box)

        return file_name_box

    def make_bar_chart(self) -> str:
        file_name_bar = "resources/dominant_colors2.svg"

        bar = np.ones((50, 500, self.NB_CLUSTERS), dtype="uint")
        plt.figure(figsize=(12, 8))
        plt.title("Proportions of colors in the image")

        start = 0
        for color in self.p_and_c:
            end = start + (color['percent'] * bar.shape[1])
            bar[:, round(start):round(end)] = color['rgb']
            start = end

        plt.imshow(bar)
        plt.xticks([])
        plt.yticks([])

        plt.savefig(file_name_bar)

        return file_name_bar

    def make_final_output(self) -> str:
        file_name_final = "resources/image_with_blocks.png"

        tmp_arr = self.np_arr.copy()
        rows = tmp_arr.shape[1]
        cols = tmp_arr.shape[0]

        cv2.rectangle(
            tmp_arr,
            (rows//2-250, cols//2-90),
            (rows//2+250, cols//2+110),
            (255, 255, 255),
            -1
        )
        cv2.putText(
            tmp_arr,
            "Most dominant colors in the satellite image",
            (rows//2-230, cols//2-40),
            cv2.FONT_HERSHEY_DUPLEX,
            0.64,
            (0, 0, 0),
            1,
            cv2.LINE_AA
        )

        start = rows//2-220
        for i, color in enumerate(self.p_and_c):
            end = start + 135
            tmp_arr[cols//2:cols//2+70, start:end] = color['rgb']
            cv2.putText(
                tmp_arr,
                str(i+1),
                (start+55, cols//2+45),
                cv2.FONT_HERSHEY_DUPLEX,
                1,
                (0, 0, 0),
                1,
                cv2.LINE_AA
            )
            start = end + 20

        Image.fromarray(tmp_arr, 'RGB').save(file_name_final)

        return file_name_final


class WeatherData():
    def __init__(self, lat: float, lon: float) -> None:
        self.lat = lat
        self.lon = lon
        self.get_and_set_data_from_api()

    def get_and_set_data_from_api(self) -> None:
        weather_url = "https://api.openweathermap.org/data/2.5/onecall"
        parameters = {
            'lat': self.lat,
            'lon': self.lon,
            'exclude': "current,minutely,hourly",
            'appid': "4b62311580df9e696fb322cf5208c520",
            'units': "metric"
        }
        r = requests.get(weather_url, params=parameters)
        req_data = r.json()

        self.dates = [datetime.fromtimestamp(day['dt']) for day in req_data['daily']]
        self.temperature = [day['temp']['day'] for day in req_data['daily']]
        self.humidity = [day['wind_speed'] for day in req_data['daily']]
        self.rain = [day.get('rain', 0) for day in req_data['daily']]
        self.rain_p = [day['pop'] for day in req_data['daily']]
        self.sunlight = [day['uvi'] for day in req_data['daily']]


def timer(func):
    def timer_wrapper(*args, **kwargs):
        start = time()
        res = func(*args, **kwargs)
        end = time()
        logging.info(f"{func.__name__} took {end-start} sec")
        return res
    return timer_wrapper


if __name__=="__main__":
    # lat, lon = 45.5, 9.2 # perform tests on user input
    # lat, lon = 41.85, -87.65 # perform tests on user input
    lat, lon = 38.219693, -94.259806 # perform tests on user input

    data = CollectedData(lat=lat, lon=lon)
    # data.imgs[0].run_color_analysis()

    print(data.weather_data)
