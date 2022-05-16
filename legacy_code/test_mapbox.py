import math
import requests
import shutil


#free version of the API offers 750k requests a month


# Get the y tile value based on a latitude value
def latToTile(latDeg, zoom):
    latRadians = math.radians(latDeg)
    n = 2.0 ** zoom
    return int((1.0 - math.asinh(math.tan(latRadians)) / math.pi) / 2.0 * n)

# Get the x tile value based on a longitude value
def lonToTile(lonDeg, zoom):
    n = 2.0 ** zoom
    return int((lonDeg + 180.0) / 360.0 * n)


# Download an image for a specified location
def getImage(latitude, longitude, zoom, accessToken):
    url = ("https://api.mapbox.com/v4/" + "mapbox.satellite/" + 
           str(zoom) + "/" + 
           str(lonToTile(longitude, zoom)) + "/" + 
           str(latToTile(latitude, zoom)) + 
           "@2x.png?access_token=" + accessToken
           )

    print(url)

    imageName = "images/" + str(latitude) + "," + str(longitude) + ".png"

    response = requests.get(url, stream=True)
    print(response)
    print(type(response))
    print(dir(response))
    
    with open(imageName, "wb") as image:
        shutil.copyfileobj(response.raw, image)
    del response
    
getImage(
    latitude=38.019693,
    longitude=-94.259806,
    zoom=11,
    accessToken="pk.eyJ1IjoiY29tZXNjaGZmciIsImEiOiJjbDJhN2FkbGkwMm94M2Nxcmljd2RvbWV0In0.bNDr3fbOcrn7QK2xYOeR2g"
)
