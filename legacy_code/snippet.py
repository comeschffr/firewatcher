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
create_temperature_chart(mock_data)

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
create_humidity_rain_chart(mock_data)


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
create_wind_chart(mock_data)


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
create_sunlight_chart(mock_data)