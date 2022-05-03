import matplotlib.pyplot as plt
import os
from datetime import datetime
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import cm


example_data = [100, 120, 134] #change


class FireWatcher_Report():
    
    def __init__(self, folder_path):
        self.rain_chart_path = ""
        self.temperature_chart_path = ""
        self.wind_chart_path = ""
        self.title = ""
        
    def __create_rain_chart(self) -> int:
        
        pass

    def __create_temp_chart(self) -> int:
        
        pass

    def __create_wind_chart(self) -> int:
        
        pass

    def create_pdf_report(self) -> str:
        
        report_path = ""

        # create charts
        self.rain_chart_path = self.__create_rain_chart()
        # etc..

        # create pdf file
        return report_path



def create_barchart(data, type: str) -> str:

    '''
    Creates a bar chart with the input data (format TBD)
    and saves it as a png file.
    Returns the path of the file
    '''
    timestamp = datetime.now().strftime('%d-%m-%Y-%H-%M-%S')
    output_path = os.path.join("images/", type + timestamp + ".png")
    days_label = ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8'] # change
    chart_data = data # TO avoid altering the var being passed
    dataset_size = len(data)

    if dataset_size>8:
        chart_data = data[:8]

    elif dataset_size<8:
        days_label = days_label[:dataset_size]

    fig = plt.figure()
    
    plt.title(str(dataset_size) + '-day ' + type + ' Forecast')
    plt.bar(days_label, chart_data)
    plt.xlabel('Days')
    plt.ylabel(type + ' Level')
    plt.savefig(output_path)

    return output_path

def create_plot(data, type: str) -> str:
    
    '''
    Creates a plot chart with the input data (format TBD)
    and saves it as a png file.
    Returns the path of the file
    '''

    timestamp = datetime.now().strftime('%d-%m-%Y-%H-%M-%S')
    output_path = os.path.join("images/", type + timestamp + ".png")
    days_label = ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8'] # change
    chart_data = data # TO avoid altering the var being passed
    dataset_size = len(data)

    # Checking that the lists for the chart have identical size

    if dataset_size>8:
        chart_data = data[:8]

    elif dataset_size<8:
        days_label = days_label[:dataset_size]

    fig = plt.figure()
    plt.title(str(dataset_size) + '-day ' + type + ' Forecast')
    plt.plot(days_label, chart_data)
    plt.xlabel('Days')
    plt.ylabel(type + ' Level')
    plt.savefig(output_path)

    return output_path

def create_pdf_report():
    
    '''
    Creates a PDF file with the information on the place and graphics
    '''

    # create charts

    # create pdf file

    margin_x = 2 * cm
    margin_y = 2 * cm
    page_size = (21 * cm, 29.7 * cm)

    canvas = Canvas("output_pdf.pdf", pagesize=page_size) # Change
    canvas.setFont("Helvetica", 12)
    canvas.drawString(margin_x, page_size[1] - margin_y, "FireWatch Report")
    canvas.drawImage('images/Temperature03-05-2022-20-36-03.png',100, 100)
    canvas.save()

    return None

create_pdf_report()

#todo
    # Charts
        # Decide on which dataype to use to pass argument
            # Simples list
            # WeatherData object (create)
        # Decide on whether to create a generic functoin to handle
        # all types of graphics (to use with an *args wrapper)
    # PDF
        # Finish drawing the images and strings in the 
        # agreed upon layout
    # Scoring Formula
        # TBD
    # 