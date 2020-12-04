"""
@author: Jemima Morris
License: "GPL"
Date created: 18/11/20
"""
import json
from json import dumps
import time
import sched
import logging
import pyttsx3
from flask import Flask, render_template, request
import requests
from requests import get
from time_conversions import hhmm_to_seconds
from time_conversions import current_time_hhmm

# load the configuration file with the API keys and the location
with open('config.json', 'r') as f:
    json_file = json.load(f)
API_keys = json_file["API_keys"]
location = json_file["location"]

# setting up the logger, Flask and the scheduler
logging.basicConfig(filename="system.log", level=logging.DEBUG)
app = Flask(__name__)
engine = pyttsx3.init()
s = sched.scheduler(time.time, time.sleep)

# declaring global list variables
notifications = []
alarms = []


def news(api_key):
    """
    This function prints the news articles onto the html page.
    It takes in the API key from the config.json file and using the url to the news source
    allows the news articles to be displayed on the html page.
    Parameters: api_key: takes in the unique API key from the config.json file
    Returns: none
    """

    base_url = 'https://newsapi.org/v2/top-headlines?sources=bbc-news'
    complete_url = base_url + "&apiKey=" + api_key
    response = requests.get(complete_url).json()
    articles = response["articles"]
    # declaring a list of titles for each news article
    titles = []
    length = len(articles)
    # iterating through each article and adding it to the list
    for article in articles:
        titles.append(article["title"])
    # adding all articles to the global variable notifications
    for i in range(0, length):
        all_news = dict()
        all_news['title'] = "News"
        all_news['content'] = (titles[i])
        notifications.append(all_news)


def weather(city_name, api_key):
    """
    This function displays the weather on the html page.
    Parameters: city_name, api_key: takes in the unique API key and the city name
                that is stored in the config.json file
    Returns: none
    """
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url).json()
    # checking for the 404 error code
    if response['cod'] != '404':
        main_response = response['main']
        current_temperature = main_response['temp']
        current_pressure = main_response["pressure"]
        current_humidity = main_response["humidity"]
        weather_response = response["weather"]
        weather_description = weather_response[0]["description"]
        weather_update = dict()
        weather_update['title'] = "Weather"
        weather_update['content'] = ("Temperature (K): " + str(current_temperature) +
                                     "\n Atmospheric Pressure (hPa): " + str(current_pressure) +
                                     "\n Humidity (%): " + str(current_humidity) +
                                     "\n Description: " + str(weather_description))
        # adding the weather update to the global variable notifications
        notifications.append(weather_update)


def corona(notifications):
    """
    This function displays the coronavirus information on the notification page by
    filtering, structuring and formatting the information to get it displayed.
    Parameters: notifications: the global notifications variable
    Returns: none
    """
    endpoint = "https://api.coronavirus.data.gov.uk/v1/data"
    area_type = "nation"
    area_name = "england"

    # filters the data in response to a request
    filters = [
        f"areaType={area_type}",
        f"areaName={area_name}"
    ]

    # structures the data accordingly and gets the data for each value
    structure = {
        "date": "date",
        "areaName": "areaName",
        "areaCode": "areaCode",
        "newCasesByPublishDate": "newCasesByPublishDate",
        "cumCasesByPublishDate": "cumCasesByPublishDate",
        "newDeathsByDeathDate": "newDeathsByDeathDate",
        "cumDeathsByDeathDate": "cumDeathsByDeathDate"
    }

    api_params = {
        "filters": str.join(";", filters),
        "structure": dumps(structure, separators=(',', ':')),
        "latestBy": "newDeathsByDeathDate"
    }

    # formats the coronavirus updates to improve user readability
    formats = ["csv"]
    for fmt in formats:
        api_params["format"] = fmt
        response = get(endpoint, params=api_params)
        # tests that the status code is 200 and therefore working
        assert response.status_code == 200, f"Failed request for {fmt}: {response.text}"
        response_covid = (response.content.decode())
        # adding the corona dictionary to the global variable 'notifications'
        corona_update = dict()
        corona_update['title'] = "Coronavirus Update"
        corona_update['content'] = response_covid
        notifications.append(corona_update)


def alarm(alarm_time, alarm_title):
    """
    This function creates an alarm.
    It uses a delay to create the concept of an alarm. It uses a speech engine to
    read out the announcement notifications.
    Parameters: alarm_time, alarm_title: the time and label the user inputs on the html.
    Returns: none
    """
    # creating an alarm
    if alarm_time:
        alarm_hhmm = alarm_time[-5:-3] + ':' + alarm_time[-2:]
        delay = hhmm_to_seconds(alarm_hhmm) - hhmm_to_seconds(current_time_hhmm())
        news_box = request.args.get("news")
        weather_box = request.args.get("weather")
        covid_box = request.args.get("covid")
        # speech provided if textbox is checked
        if news_box:
            s.enter(int(delay), 1, announce, [notifications[2]['content']])
        elif weather_box:
            s.enter(int(delay), 1, announce, [notifications[2]['content']])
        elif covid_box:
            s.enter(int(delay), 1, announce, [notifications[2]['content']])
        else:
            s.enter(int(delay), 1, announce, [notifications[1]['content']])
        alarm_hhmm = alarm_time[-5:-3] + ':' + alarm_time[-2:]
        alarms.append({'title': alarm_title, 'content': alarm_hhmm})


@app.route('/')
@app.route('/index')
def index():
    """
    This function runs the program.
    Parameters: none
    Returns: render_template("template.html", image="image.jpg", notifications=notifications,
                           alarms=alarms):
             displays the html template.
    """
    s.run(blocking=False)
    alarm_time = request.args.get("alarm")
    alarm_title = request.args.get("two")
    weather(location['city'], API_keys['weather'])
    corona(notifications)
    news(API_keys['news'])
    alarm(alarm_time, alarm_title)
    return render_template("template.html", image="image.jpg", notifications=notifications,
                           alarms=alarms)


def announce(announcement):
    """
    Uses pyttsx3 to generate a text-to-speech engine to say an announcement
    out loud.
    Parameters: announcement: takes in the text to be spoken and reads it out.
    Returns: none
    """
    try:
        engine.endLoop()
    except:
        pass
    engine.say(announcement)
    engine.runAndWait()


if __name__ == '__main__':
    app.run(debug=True)
