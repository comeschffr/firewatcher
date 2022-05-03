import os
from PIL import Image
import matplotlib.pyplot as plt
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader, cm

mock_graph_links = {
    "temperature":"images/temp.jpeg",
    "rain": "images/rain.jpeg",
    "sunlight": "images/sunlight.jpeg",
    "wind": "images/wind.jpeg"
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
    ax.bar(day_labels, rain_data, color="aqua", label="rain")
    ax.set_ylabel("Rain volume (in mm)")
    ax.legend(loc=0)
    ax2 = ax.twinx()
    ax2.plot(day_labels, hum_data, marker='o', color="lightsteelblue", label="humidity")
    ax2.set_ylabel("Humidity (in %)")
    ax2.legend(loc=0)
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
    plt.ylim(top=10)
    plt.savefig(graph_filename)
    plt.clf()

    return graph_filename

def resize_and_convert(path, newsize = (250,250)):
    img_PIL = Image.open(path)
    img_PIL = img_PIL.resize(newsize)
    img_RL = ImageReader(img_PIL)
    return img_RL

def create_pdf_report(graphs_link: dict):
    
    '''
    Creates a PDF file with the information on the place and graphics
    '''

    # create pdf file

    margin_x = 1 * cm
    page_size = (21 * cm, 29.7 * cm)
    page_height = page_size[1]
    size = 30
    buffer = 1 * cm

    img = Image.open('images/satelite.png')
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

    return None