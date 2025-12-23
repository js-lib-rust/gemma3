import requests


def simple_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': lat,
        'longitude': lon,
        'current': 'temperature_2m,weather_code,wind_speed_10m',
        'timezone': 'auto'
    }

    response = requests.get(url, params=params)
    data = response.json()

    current = data['current']
    print(f"Temperature: {current['temperature_2m']}°C")
    print(f"Weather Code: {current['weather_code']}")
    print(f"Wind Speed: {current['wind_speed_10m']} km/h")


simple_weather(47.18053804019403, 27.48875276837502)