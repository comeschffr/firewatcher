import os
import base64
import datetime
import jinja2

HTML_TEMPLATE_PATH = "report_template.html"

mock_images = {
    'satelite_1': 'images/satelite_1.png',
    'satelite_2': 'images/satelite_2.png',
    'satelite_1_color' : 'images/color.png',
    'satelite_2_color' : 'images/color.png',
    'temp_chart' : "images/temp.jpeg",
    'rain_chart' : 'images/rain.jpeg',
    'wind_chart' : 'images/wind.jpeg',
    'sunlight_chart' : "images/sunlight.jpeg"
}

mock_location_data = {
    "latitude": 34.5432,
    "longitude": 37.5995,
    "date_image_1": "05/08/2021",
    "date_image_2": "05/11/2021"
}

class FireWatcher_Report():
    def __init__(self, 
                file_name: str = None,
                images: dict = None, 
                weather_data: dict = None,
                template_path: str = HTML_TEMPLATE_PATH,
                ):
        self.template_path = template_path
        self._images = images or {}
        self._weather_data = weather_data or {}
        self.file_name = self._name_file(file_name)
        self.template = None

    def add_image(self, img_label: str, img_path: str) -> None:
        self._images[img_label] = img_path

    def _timestamp(self) -> str:
        
        return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    def _name_file(self, file_name: str) -> str:
        if file_name is None:
            return self._timestamp() + ".html"

        if file_name[-5] == ".html":
            return file_name
        
        return file_name + ".html"

    def _image_file_path_to_base64_string(self, filepath: str) -> str:
        with open(filepath, 'rb') as f:

            return base64.b64encode(f.read()).decode()
    
    def _convert_images_to_byte64(self) -> None:
        for image in self._images:
            self._images.update({image : self._image_file_path_to_base64_string(os.path.abspath(str(self._images[image])))})

    def _load_template(self) -> None:
        templateLoader = jinja2.FileSystemLoader(searchpath="./")
        templateEnv = jinja2.Environment(loader=templateLoader)
        self.template = templateEnv.get_template(self.template_path)

    def make_report(self) -> str:
        self._load_template()
        self._convert_images_to_byte64()
        self._images.update({"timestamp" : datetime.datetime.now().strftime("%m/%d/%Y")})
        html_str = self.template.render(self._images | self._weather_data)
      
        with open(self.file_name + ".html", "w") as f:
            f.write(html_str)
            f.close()

        return os.path.abspath(self.file_name)

def main():
    
    # passing the ready-made dictionary thorugh the constructor
    report = FireWatcher_Report(weather_data = mock_location_data, images = mock_images)
    
    # initiating w/o images and adding them after

    #for img in images:
     #   report.add_image(img, images[img])

    print(report.make_report())

if __name__ == "__main__":
    main()