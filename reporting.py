import os
import base64
import datetime
import pdfkit
import jinja2


HTML_TEMPLATE_PATH = "ft2.html"

images = {
    'satelite_1': 'satelite_1.png',
    'satelite_2': 'sunlight.jpeg',
}

mock_location_data = {
    "latitude": 34.5432,
    "longitude": 37.5995,
    "date_image_1": "05/08/2021",
    "date_image_1": "05/11/2021"
}

class PDFReport():
    def __init__(self, 
                file_name: str = None,
                images: dict = None, 
                weather_data: dict = None,
                template_path: str = HTML_TEMPLATE_PATH,
                ):
        self.template_path = template_path
        self.__images = images or {}
        self.__weather_data = weather_data or {}
        self.file_name = file_name or self.__timestamp() + ".pdf"
        self.template = None

    def add_image(self, img_label: str, img_path: str) -> None:
        self.__images[img_label] = img_path

    def __timestamp(self) -> None:
        
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    def __image_file_path_to_base64_string(self, filepath: str) -> str:
        with open(filepath, 'rb') as f:

            return base64.b64encode(f.read()).decode()
    
    def __convert_images_to_byte64(self) -> None:
        for image in self.__images:
            self.__images.update({image : self.__image_file_path_to_base64_string(os.path.abspath(str(self.__images[image])))})

    def __load_template(self) -> None:
        templateLoader = jinja2.FileSystemLoader(searchpath="./")
        templateEnv = jinja2.Environment(loader=templateLoader)
        self.template = templateEnv.get_template(self.template_path)

    def __convert_html_to_pdf(self, html_str: str) -> None:
        path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
        pdfkit.from_string(html_str, self.file_name, configuration=config)

    def create_report(self) -> None:
        self.__load_template()
        self.__convert_images_to_byte64()
        html_str = self.template.render(self.__images)
        self.__convert_html_to_pdf(html_str)

# Testing
# Decide on how to implement input to add image
# either through dict or kwargs

#report = PDFReport()
#report.add_image("satelite_1", images.get("satelite_1"))
#report.add_image("satelite_2", images.get("satelite_2"))
#report.create_report()