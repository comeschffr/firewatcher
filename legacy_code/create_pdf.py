from datetime import datetime

from PIL import Image
import matplotlib.pyplot as plt
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4


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

mock_location_data = {
    "latitude": 34.5432,
    "longitude": 37.5995,
    "date_image_1": "05/08/2021",
    "date_image_1": "05/11/2021"
}

mock_graph_paths = {
    "img_sat-1": "resources/satelite.png",
    "img_sat-2": "resources/satelite.png",
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


def resize_and_convert_image(path: str, newsize = (250,250)) -> ImageReader:
    img_PIL = Image.open(path)
    img_PIL = img_PIL.resize(newsize)
    img_RL = ImageReader(img_PIL)

    return img_RL

def create_pdf_report(graphs_link: dict, file_name: str) -> str:
    # Document Variables - pass as a dict?
    page_size = A4
    margin_x = 1 * cm
    margin_y = 1 * cm
    page_height = page_size[1]
    title_size = 20
    buffer_horizontal = 1 * cm
    buffer_vertical = 1 * cm
    map_size = 200 
    chart_size = 220
    section_buffer = 3.5 * cm
    text_box_border_top = 0.5 * cm
    text_box_border_left = 0.25 * cm
    text_box_height = 3.5 * cm 

    # Create PDF object
    output_pdf = Canvas(file_name + ".pdf", pagesize=page_size)
    
    # Add titles and text
    output_pdf.setLineWidth(2)
    output_pdf.setFont("Helvetica-Bold", title_size)
    output_pdf.drawCentredString(page_size[0]/2.0, page_height - margin_y - buffer_vertical/2, "FireWatcher Report")

    output_pdf.rect(
                    margin_x + map_size*2 + buffer_horizontal, #x_pos
                    page_height - margin_y - buffer_vertical - map_size,
                    4*cm,
                    map_size,
                    stroke = 1
    )

    text_coordinates = output_pdf.beginText()
    text_coordinates.setTextOrigin(
                                margin_x + map_size*2 + buffer_horizontal + text_box_border_left, #x_pos
                                page_height - margin_y - buffer_vertical - text_box_border_top
    )
    text_coordinates.setFont('Helvetica', 12)
    text_coordinates.textLine("Latitude: " + str(graphs_link.get("latitude")))
    text_coordinates.textLine("Longitude: " + str(graphs_link.get("longitude")))
    text_coordinates.textLine("Picture 1 Date")
    text_coordinates.textLine(str(mock_location_data.get("date_image_1")))
    text_coordinates.textLine("Picture 2 Date")
    text_coordinates.textLine(str(mock_location_data.get("date_image_2")))
    text_coordinates.textLine("Danger Score: 71")
    output_pdf.drawText(text_coordinates)

    # Add Images
    img_sat_1 = resize_and_convert_image(graphs_link.get('img_sat-1'), (map_size, map_size))
    output_pdf.drawImage(img_sat_1, 
                        margin_x,  # x_pos
                        page_height - margin_y - buffer_vertical - map_size) # y_pos

    img_sat_2 = resize_and_convert_image(graphs_link.get('img_sat-2'), (map_size, map_size))
    output_pdf.drawImage(img_sat_2, 
                        margin_x + map_size + buffer_horizontal/2, # x_pos
                        page_height - margin_y - buffer_vertical - map_size) # y_pos

    img_temp = resize_and_convert_image(graphs_link.get('temperature'), (chart_size, chart_size))
    output_pdf.drawImage(img_temp, 
                        margin_x + buffer_horizontal,
                        page_height - buffer_vertical*3 - chart_size*2 - section_buffer)
    
    img_rain = resize_and_convert_image(graphs_link.get('rain'),(chart_size, chart_size))
    output_pdf.drawImage(img_rain, 
                        margin_x + chart_size + buffer_vertical + + buffer_horizontal, 
                        page_height - buffer_vertical*3 - chart_size*2 - section_buffer)

    img_wind = resize_and_convert_image(graphs_link.get('wind'), (chart_size, chart_size))
    output_pdf.drawImage(img_wind,
                        margin_x + + buffer_horizontal,
                        page_height - buffer_vertical*3 - chart_size*3 - section_buffer)

    img_sunlight = resize_and_convert_image(graphs_link.get('sunlight'), (chart_size, chart_size))
    output_pdf.drawImage(img_sunlight, 
                        margin_x + chart_size + buffer_vertical + + buffer_horizontal,
                        page_height - buffer_vertical*3 - chart_size*3 - section_buffer)
    
    output_pdf.save()

    return file_name

create_pdf_report(mock_graph_paths, "pdf_tests/" + datetime.now().strftime("%H-%M-%S"))
