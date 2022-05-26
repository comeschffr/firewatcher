import base64
import datetime
import os

import jinja2


class FinalReport():
    def __init__(
        self,
        template_path: str,
        location_data: dict,
        risk_index: float,
        folder: str,
        file_name: str = None,
    ) -> None:
        self.template_path = template_path
        self._location_data = location_data
        self._risk_index = str(round(risk_index*100))
        self.file_name = (
            file_name
            if file_name
            else f"{folder}/firewatcher_report_"+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+".html"
        )
        self.file_name = os.path.abspath(self.file_name)
        self._resources = {}

    def add_resources(self, resources: dict) -> None:
        """
        Load resources to the class to pass them to the Jinja template
        """
        for resource_name, resource_path in resources.items():
            self._resources[resource_name] = self._image_file_path_to_base64_string(resource_path)

    def _image_file_path_to_base64_string(self, filepath: str) -> str:
        """
        Encode images to base64 to ensure data integrity
        """
        with open(filepath, 'rb') as f:
            return base64.b64encode(f.read()).decode()

    def _load_template(self) -> None:
        templateLoader = jinja2.FileSystemLoader(searchpath="./")
        templateEnv = jinja2.Environment(loader=templateLoader)
        self.template = templateEnv.get_template(self.template_path)

    def generate(self) -> None:
        """
        Create HTML page using Jinja templates
        """
        self._load_template()
        self._resources["timestamp"] = datetime.datetime.now().strftime("%m/%d/%Y")
        self._resources["risk_index"] = self._risk_index
        self.html_str = self.template.render(self._resources | self._location_data)

    def save(self) -> None:
        """
        Write HTML file object to disk
        """
        with open(self.file_name, "w") as f:
            f.write(self.html_str)
