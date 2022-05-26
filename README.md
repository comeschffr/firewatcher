# FireWatcher

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀<br/>
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⡾⠛⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀<br/>
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠟⢁⣴⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀<br/>
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⡿⠃⡰⠃⣏⠀⢿⡆⡀⠀⠀⠀⠀⠀⠀⠀⠀<br/>
⠀⠀⠀⠀⠀⠀⢤⣤⣤⣴⣿⠁⢰⠃⠀⢹⡀⠘⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀<br/>
⠀⠀⠀⠀⠀⠀⠀⢿⡌⠙⢿⠀⡟⠀⠀⠀⢷⡀⠈⠹⣷⡀⠀⠀⠀⠀⠀⠀<br/>
⠀⠀⠀⠀⠀⢶⣦⣼⡇⢰⢤⡀⡇⠀⠀⠀⠘⠷⢷⡀⠙⣷⡄⠀⠀⠀⠀⠀<br/>
⠀⠀⠀⠀⠀⣸⡏⠙⠀⣼⠀⠙⠃⠀⠀⠀⠀⠀⠈⢧⡀⠈⢿⣤⣶⠀⠀⠀<br/>
⠀⠀⠀⠀⣴⡟⢠⢶⣰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠳⡄⠘⠿⣿⡆⠀⠀<br/>
⠀⠀⢀⣼⠏⢠⠏⠈⠃⠀⠀⠀⠀⠀⢸⢳⡀⢀⠀⠀⠀⢹⣤⡄⠘⣿⡀⠀<br/>
⠀⠀⣼⡏⢀⡏⠀⠀⠀⠀⠀⠀⣄⣀⢸⠀⠉⠋⠳⡄⠀⠀⠁⢻⡀⠹⣧⠀<br/>
⠀⣸⡿⠀⡞⠀⠀⠀⣀⠀⢀⡼⠃⠈⠛⠀⠀⠀⠀⠹⣆⠀⠀⠈⡇⠀⣿⡆<br/>
⠀⣿⠇⢸⠁⠀⠀⣰⠋⠳⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⡀⠀⠀⣿⠀⣿⡇<br/>
⢸⣿⠀⣿⠀⠀⢠⠇⠀⠀⠀⠀Welcome⠀⠀⠀⢸⡇⠀⠀⡟⠀⣿⠇<br/>
⠈⣿⠀⢿⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀to⠀⠀⠀⠀⠀⠀⣸⣇⠀⣸⠃⢰⣿⡀<br/>
⠀⢿⣇⠸⣇⠀⢸⡄⠀⠀⠀  FireWatcher⠀ ⣹⢃⣴⣧⡴⢿⣿⠃ <br/>
⠀⠈⢿⡄⠘⢦⡈⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠃⢀⡽⠋⣠⣿⠋⠀ <br/>
⠀⠀⠈⠻⣦⣀⠙⢮⣳⢤⡀⠀⠀⠀⠀⢀⣀⣴⡿⠶⠊⣉⣴⡾⠋⠁<br/>
⠀⠀⠀⠀⠈⠛⢷⣦⣄⣉⡉⠙⠛⠋⠉⢉⣉⣠⣤⣶⡿⠟⠉⠀⠀<br/>
⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⠛⠻⠿⠿⠿⠟⠛⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀ <br/>


FireWatcher is a terminal-based application that gives the user insights about the likelihood of wildfires in a given region, by combining satellite imagery (Landsat 9) and meteorological data.

The application is structured in 3 stages:
+ **Data Collection** - *collect_data.py*
&nbsp;&nbsp;&nbsp;&nbsp;takes latitude/longitude coordinates as inputs
&nbsp;&nbsp;&nbsp;&nbsp;collects satellite imagery from Google Earth Engine
&nbsp;&nbsp;&nbsp;&nbsp;collects weather data from OpenWeatherMap
+ **Data Analysis** - *image_analysis.py*
&nbsp;&nbsp;&nbsp;&nbsp;finds dominant color in each satellite image using K-means ML algorithm
&nbsp;&nbsp;&nbsp;&nbsp;uses custom-made formula to assess overall wildfire risk
+ **Results Summary** - *final_report.py*
&nbsp;&nbsp;&nbsp;&nbsp;Generates an HTML report containing the analysis' result (plots, images, calculations). We use jinja templates to pass data from python to the HTML file.

<br/>

#### Video demo

https://youtu.be/kZLAx3ty8mk (unlisted video)

<br/>

---

### Quick Start guide

Clone this repository using

`git clone git@github.com:comeschffr/firewatcher.git`

then run these following command to install dependencies

`cd firewatcher`
`pip install -r requirements.txt`

Create an API key on OpenWeatherMap
https://home.openweathermap.org/api_keys
Once you have the API key, add it to `config.ini` under the variable `api_key`

Install gcloud CLI, a mandatory tool to use any Google API
You can follow the instructions here: https://cloud.google.com/sdk/docs/install

Here it is, you are all set!
Just run
`python main.py` or `python3 main.py` (depending on your terminal)
[if you run the program for the first time on your machine, you should uncomment `ee.Authenticate()` in `collect_data.py`, you can comment it out back again afterward]

HINT: the applicaiton works better with US coordinates

---

This project was achieved by three Bocconi students as the final project of the course 30590 ADVANCED PYTHON PROGRAMMING FOR ECONOMICS, MANAGEMENT AND FINANCE 
