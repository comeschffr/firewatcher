from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from PIL import Image


mock_graph_links = {
    "temperature":"images/temp.jpeg",
    "rain": "images/rain.jpeg",
    "sunlight": "images/sunlight.jpeg",
    "wind": "images/wind.jpeg"
}

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

create_pdf_report(mock_graph_links)