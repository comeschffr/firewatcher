import logging
import uuid
from datetime import datetime
from time import time

import ee
import numpy as np
import requests
from PIL import Image


logging.basicConfig(level=logging.INFO)


def timer(func):
    def timer_wrapper(*args, **kwargs):
        start = time()
        res = func(*args, **kwargs)
        end = time()
        logging.info(f"{func.__name__} took {end-start} sec")
        return res
    return timer_wrapper


@timer
def initialize_gee() -> None:
    # ee.Authenticate()
    logging.info("Initializing Google Earth Engine...")
    ee.Initialize()
    logging.info("Google Earth Engine initialized successfully!")


def get_aoi(lat: float, lon: float) -> ee.Geometry.Polygon:
    aoi = ee.Geometry.Polygon(
        [[
            [lon-0.1, lat+0.1],
            [lon-0.1, lat-0.1],
            [lon+0.1, lat-0.1],
            [lon+0.1, lat-0.1],
        ]],
        None,
        False
    )
    return aoi


@timer
def get_most_recent_imgs(aoi: ee.Geometry.Polygon) -> ee.Image:
    collection = (
        ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
        .filterBounds(aoi)
        .filter("CLOUD_COVER < 55")
        .sort('system:time_start', False)
        .limit(2)
    )

    def applyScaleFactors(image):
        opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
        thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0);
        return image.addBands(opticalBands, None, True).addBands(thermalBands, None, True);

    collection = collection.map(applyScaleFactors)

    if collection.size().getInfo() < 2:
        raise ValueError("Could not find enough images for further analysis (<2 images)")

    list_of_imgs = collection.toList(2)

    img1 = ee.Image(list_of_imgs.get(0))
    img2 = ee.Image(list_of_imgs.get(1))

    return img1.select("SR_B4", "SR_B3", "SR_B2"), img2.select("SR_B4", "SR_B3", "SR_B2")


def get_img_date(img: ee.Image) -> datetime:
    timestamp = img.getInfo()['properties']['system:time_start']
    return datetime.fromtimestamp(timestamp/1000)


@timer
def get_img_download_url(img: ee.Image, aoi: ee.Geometry.Polygon) -> str:
    url = img.getDownloadURL(
        {
            'region': aoi,
            'dimensions': "1000x1000", # 1365x1365 max resolution for authorized request size
            'format': "npy",
        }
    )
    logging.info(f"Found URL successfully: {url}")
    return url


@timer
def download_file(url: str, base_filename: str, lat: float, lon: float, id: int) -> str:
    logging.info(f"Requesting image {str(id)} at {url}...")
    r = requests.get(url)

    curr_date = datetime.now().strftime("%m-%d-%Y_%H%M%S")
    filepath = (
        "images/" + base_filename + "_" +
        str(lat) + "_" + str(lon) + "_" +
        curr_date + "_" + str(id) + ".arr"
    )
    logging.info(f"Saving raw request content to {filepath}")
    with open(filepath, "wb") as f:
        f.write(r.content)

    return filepath


def to_np_arr(filepath: str) -> np.array:
    logging.info("Creating numpy array from bytes response...")

    with open(filepath, "rb") as f:
        arr = np.lib.format.read_array(f)

    return np.array(arr.tolist())


def to_rgb_img(arr: np.array) -> Image:
    arr[arr < 0] = 0
    arr[arr > 0.3] = 0.3

    rgb_img = (255*(arr/0.3)).astype('uint8')
    img = Image.fromarray(rgb_img, 'RGB')

    return img


if __name__=="__main__":
    initialize_gee()

    # lat, lon = 45.5, 9.2 # perform tests on user input
    # lat, lon = 41.85, -87.65 # perform tests on user input
    lat, lon = 38.219693, -94.259806 # perform tests on user input
    aoi = get_aoi(lat, lon)
    img1, img2 = get_most_recent_imgs(aoi)

    url1 = get_img_download_url(img1, aoi)
    url2 = get_img_download_url(img2, aoi)

    base_filename = str(uuid.uuid4())[:8]
    filepath1 = download_file(url1, base_filename, lat, lon, 1)
    filepath2 = download_file(url2, base_filename, lat, lon, 2)

    # filepath1 = "images/e1f8a450_05-02-2022_133819_1.arr"
    # filepath2 = "images/e1f8a450_05-02-2022_133852_2.arr"
    arr1 = to_np_arr(filepath1)
    arr2 = to_np_arr(filepath2)

    img1 = to_rgb_img(arr1)
    img1.show()
    img1.save(filepath1.replace("arr", "png"))

    img2 = to_rgb_img(arr2)
    img2.show()
    img2.save(filepath2.replace("arr", "png"))
