import ee
import logging
from datetime import datetime, timedelta

from test_mapbox import latToTile


logging.basicConfig(level=logging.DEBUG)

logging.info("Initializing Earth Engine client...")
try:
    ee.Initialize()
    logging.info("Initialization successful")
except:
    logging.critical("Failed to initialize client :(")


def verify_bbox(bbox):
    """Check that bbox is properly specified."""
    if type(bbox) != dict:
        raise Exception(
            'Malformed bounding box: must be "dict" type.\n%s' % str(bbox))

    for coord in ['xmax', 'xmin', 'ymax', 'ymin']:
        if coord not in bbox:
            raise Exception('Malformed bounding box: missing %s value' % coord)

    if bbox['xmin'] > bbox['xmax']:
        raise Exception('Malformed bounding box: xmin is greater than xmax')

    if bbox['ymin'] > bbox['ymax']:
        raise Exception('Malformed bounding box: ymin is greater than ymax')

    return True

def parse_bbox(bbox):
    """Convert a bbox dictionary to list a la [xmax, ymax, xmin, ymin]."""
    if verify_bbox(bbox):
        xmax = bbox['xmax']
        ymax = bbox['ymax']
        xmin = bbox['xmin']
        ymin = bbox['ymin']

    return [xmax, ymax, xmin, ymin]

def bbox_to_coords(bbox):
    """Convert a bbox dictionary to a list of coordinate lists, suitable for
    use as a counter-clockwise polygon geometry in Google Earth Engine."""
    xmax, ymax, xmin, ymin = parse_bbox(bbox)

    return [[xmax, ymax],
            [xmin, ymax],
            [xmin, ymin],
            [xmax, ymin],
            [xmax, ymax]]

def acqtime(feature):
    """A handler that returns the correctly formatted date, based on asset."""
    msec = feature['properties']['system:time_start']
    return datetime.fromtimestamp(msec / 1000).isoformat()

def export_image(idx, coords, cloud_score=None):
    """Returns the thumbnail URL for a given Landsat image, bounded by the
    supplied coordinates.
    Arguments
        idx: A landsat image ID
        coords: A list of coordinate pairs, closed and counter-clockwise
        sharpen: Boolean indicating whether the image should be pan-sharpened
    Example:
        export_image(
            idx='LC8_L1T_TOA/LC81270592013320LGN00',
            coords=[[0,0], [1,0], [1,1], [0,1], [0,0]],
            sharpen=True
        )
    """
    print("idx is ", idx)
    print("type idx is ", type(idx))

    thumb_params = {
        'crs': 'EPSG: 4326',
        'region': str(coords),
        'dimensions': [2048, 2048],
        'format': 'png',
        'min': 0,
        'max': 0.3,
        # 'bands': 'SR_B2,SR_B3,SR_B4',
    }
    
    img = ee.Image(idx)
    
    print("img", img)
    image_test = img

    print("cloud score in export image function is: ", cloud_score)
    final2 = dict(url = image_test.getThumbUrl(thumb_params))
    return final2


class GEEasset():
    def __init__(self, bbox, dataset):
        self.coords = bbox_to_coords(bbox)
        self.poly = ee.Geometry.Polygon(self.coords)
        self.roi = ee.Geometry.Point([-94.259806, 38.019693])
        self.coll = (
            ee.ImageCollection(dataset)
            .filterBounds(self.roi)
            .sort("CLOUD_COVER")
        )

        def applyScaleFactors(image):
            opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
            thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0)
            return image.addBands(opticalBands, None, True).addBands(thermalBands, None, True)

        self.coll = self.coll.map(applyScaleFactors)

    def id_stack(self, begin, end):
        """
        returns
        [
            {
                'date': '2021-12-12T17:54:45.206000', 
                'id': 'LANDSAT/LC09/C02/T1_L2/LC09_026033_20211212'
            },
            {
                'date': '2021-12-28T17:54:43.605000',
                'id': 'LANDSAT/LC09/C02/T1_L2/LC09_026033_20211228'
            }
        ]
        """
        stack = self.coll.filter(ee.Filter.date(begin, end)).getInfo()['features']
        return [dict(date=acqtime(x), id=x['id']) for x in stack]

    def image(self, date, cloud_score=None, offset=30):
        target_date = datetime.strptime(date, "%Y-%m-%d")
        delta = timedelta(days=offset)
        available = self.id_stack(target_date - delta, target_date + delta)
        if len(available) == 0:
            raise Exception('No imagery for specified date.')
        else:
            def _sorter(d):
                img_date = datetime.strptime(d['date'][0:19], "%Y-%m-%dT%H:%M:%S")
                return abs(img_date - target_date)

            closest = sorted(available, key=_sorter)[0]
            closest.update(
                export_image(
                    closest['id'],
                    self.coords,
                    cloud_score=cloud_score
                )
            )
            return closest


date = "2022-01-01"
lat = 38.019693
lon = -94.259806

# dataset = "LANDSAT/LC08/C01/T1_SR"
dataset = "LANDSAT/LC09/C02/T1_L2"
# dataset = "LANDSAT/LC08/C02/T1_L2"

dim = 0.1

bbox = {
    'xmin': lon - (dim / 2),
    'xmax': lon + (dim / 2),
    'ymin': lat - (dim / 2),
    'ymax': lat + (dim / 2)
}

asset = GEEasset(bbox, dataset)
print(asset)

res = asset.image(date=date)
print(res)
