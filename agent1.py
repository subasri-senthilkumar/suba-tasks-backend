import os
import requests
import dateparser
from datetime import datetime, timedelta
from fastapi import FastAPI

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

app = FastAPI(title="Agentic Weather Intelligence Agent")

def parse_user_query(query: str):
    query = query.lower()

    words = query.split()
    city = words[-1].capitalize()

    if "yesterday" in query:
        date = datetime.utcnow() - timedelta(days=1)
        mode = "historical"
    elif "tomorrow" in query:
        date = datetime.utcnow() + timedelta(days=1)
        mode = "forecast"
    else:
        date = datetime.utcnow()
        mode = "current"

    return city, date, mode

def get_current_weather(city):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )
    return requests.get(url).json()


def get_forecast_weather(city):
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )
    return requests.get(url).json()


def get_historical_weather(lat, lon, timestamp):
    url = (
        f"https://api.openweathermap.org/data/3.0/onecall/timemachine"
        f"?lat={lat}&lon={lon}&dt={timestamp}&appid={OPENWEATHER_API_KEY}&units=metric"
    )
    return requests.get(url).json()

@app.post("/chat")
def weather_agent(query: str):
    city, date, mode = parse_user_query(query)

    # Step 1: Current Weather
    if mode == "current":
        data = get_current_weather(city)
        return {
            "agent_decision": "Used Current Weather Tool",
            "response": f"It is currently {data['main']['temp']}°C in {city} with {data['weather'][0]['description']}."
        }

    elif mode == "forecast":
        data = get_forecast_weather(city)
        tomorrow_data = data["list"][8] 
        return {
            "agent_decision": "Used Forecast Weather Tool",
            "response": f"Tomorrow in {city}, the temperature will be around {tomorrow_data['main']['temp']}°C with {tomorrow_data['weather'][0]['description']}."
        }

    elif mode == "historical":
        current = get_current_weather(city)
        lat, lon = current["coord"]["lat"], current["coord"]["lon"]

        timestamp = int(date.timestamp())
        data = get_historical_weather(lat, lon, timestamp)

        temp = data["data"][0]["temp"]
        desc = data["data"][0]["weather"][0]["description"]

        return {
            "agent_decision": "Used Historical Weather Tool",
            "response": f"Yesterday in {city}, the temperature was {temp}°C with {desc}."
        }
