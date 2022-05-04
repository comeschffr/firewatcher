from datetime import datetime

from PIL import Image
import matplotlib.pyplot as plt
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm


mock_data = {
    'dates': 
        [
        datetime(2022, 5, 4, 20, 0),
        datetime(2022, 5, 5, 20, 0),
        datetime(2022, 5, 6, 20, 0),
        datetime(2022, 5, 7, 20, 0),
        datetime(2022, 5, 8, 20, 0),
        datetime(2022, 5, 9, 20, 0),
        datetime(2022, 5, 10, 20, 0),
        datetime(2022, 5, 11, 20, 0),
    ],
    'humidity': [69, 80, 91, 65, 71, 70, 69, 63],
    'rain': [5.48, 28.47, 0.12, 0, 0, 1.1, 16.72, 0],
    'rain_p': [0.97, 1, 0.49, 0, 0, 0.88, 1, 0],
    'sunlight': [7.16, 2.91, 4.49, 9.16, 0.15, 1, 1, 1],
    'temperature': [16.18, 22.14, 14.77, 20.68, 26.04, 28, 27.8, 27.78],
    'wind': [5.32, 8.74, 6.06, 7.42, 9.51, 11.19, 8.36, 7.54],
}


mock_graph_links = {
    "temperature":"resources/temperature_chart.png",
    "rain": "resources/hum_rain_chart.png",
    "sunlight": "resources/wind_chart.png",
    "wind": "resources/sunlight_chart.png"
}


def create_temperature_chart(weather_data: dict) -> str:
    graph_filename = "resources/temperature_chart.png"
    temperature_data = weather_data['temperature']
    day_labels = [dt.strftime("%m/%d") for dt in weather_data['dates']]

    plt.bar(day_labels, temperature_data, color="firebrick")  
    plt.title(str(len(temperature_data)) + '-day Temperature Forecast')
    plt.ylabel("°C")
    plt.savefig(graph_filename)
    plt.clf()

    return graph_filename


def create_humidity_rain_chart(weather_data: dict) -> str:
    graph_filename = "resources/hum_rain_chart.png"
    hum_data = weather_data['humidity']
    rain_data = weather_data['rain']
    day_labels = [dt.strftime("%m/%d") for dt in weather_data['dates']]

    fig, ax = plt.subplots()
    bar1 = ax.bar(day_labels, rain_data, color="aqua", label="rain")
    ax.set_ylabel("Rain volume (in mm)")
    ax.legend(loc=0)
    ax2 = ax.twinx()
    line1 = ax2.plot(day_labels, hum_data, marker='o', color="lightsteelblue", label="humidity")
    ax2.set_ylabel("Humidity (in %)")
    ax2.set_ylim(bottom=0, top=100)

    legends = [bar1, line1[0]]
    labs = [leg.get_label() for leg in legends]
    ax.legend(legends, labs, loc=0)

    plt.title("Rain and Humidity Forecast")
    fig.savefig(graph_filename)
    plt.clf()

    return graph_filename


def create_wind_chart(weather_data: dict) -> str:
    graph_filename = "resources/wind_chart.png"
    wind_data = weather_data['wind']
    day_labels = [dt.strftime("%m/%d") for dt in weather_data['dates']]

    plt.plot(day_labels, wind_data, marker='o', color="olivedrab")
    plt.title("Wind forecast")
    plt.ylabel("m/s")
    plt.savefig(graph_filename)
    plt.clf()

    return graph_filename


def create_sunlight_chart(weather_data: dict) -> str:
    graph_filename = "resources/sunlight_chart.png"
    sunlight_data = weather_data['sunlight']
    day_labels = [dt.strftime("%m/%d") for dt in weather_data['dates']]

    plt.bar(day_labels, sunlight_data, color="gold")
    plt.title("Sunlight forecast")
    plt.ylabel("UV index")
    plt.ylim(bottom=0, top=10)
    plt.savefig(graph_filename)
    plt.clf()

    return graph_filename

create_temperature_chart(mock_data)
create_humidity_rain_chart(mock_data)
create_wind_chart(mock_data)
create_sunlight_chart(mock_data)
print(" All charts created!")


def resize_and_convert(path, newsize = (250,250)):
    img_PIL = Image.open(path)
    img_PIL = img_PIL.resize(newsize)
    img_RL = ImageReader(img_PIL)
    return img_RL

def create_pdf_report(graphs_link: dict) -> None:
    margin_x = 1 * cm
    page_size = (21 * cm, 29.7 * cm)
    page_height = page_size[1]
    size = 30
    buffer = 1 * cm

    img = Image.open('images/76e9e3ba_38.219693_-94.259806_05-03-2022_181759_1.png')
    newsize = (250, 250)
    img2= img.resize(newsize)
    img3 = ImageReader(img2)

    canvas = Canvas("output_pdf.pdf", pagesize=page_size) # Change
    canvas.setFont("Helvetica", size)
    canvas.drawCentredString(page_size[0]/2.0, page_size[1]-50, "FireWatch Report")

    # Add Images
    canvas.drawImage(img3, margin_x, page_height-350)

    img_temp = resize_and_convert(graphs_link.get('temperature'))
    canvas.drawImage(img_temp, margin_x, page_height-570)
    
    img_rain = resize_and_convert(graphs_link.get('rain'))
    canvas.drawImage(img_rain, margin_x+250+buffer, page_height-570)

    img_wind = resize_and_convert(graphs_link.get('wind'))
    canvas.drawImage(img_wind, margin_x, page_height-570-250)

    img_sunlight = resize_and_convert(graphs_link.get('sunlight'))
    canvas.drawImage(img_sunlight, margin_x+250+buffer, page_height-570-250)
    
    canvas.save()

    return

create_pdf_report(mock_graph_links)
