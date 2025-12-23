import requests
import json
from datetime import datetime


def get_current_weather(latitude, longitude):
    """
    Get current weather information using Open-Meteo API
    """
    # Open-Meteo API endpoint for current weather
    url = "https://api.open-meteo.com/v1/forecast"

    # Parameters for the API request
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'current': [
            'temperature_2m',
            'relative_humidity_2m',
            'apparent_temperature',
            'is_day',
            'precipitation',
            'rain',
            'showers',
            'snowfall',
            'weather_code',
            'cloud_cover',
            'pressure_msl',
            'surface_pressure',
            'wind_speed_10m',
            'wind_direction_10m',
            'wind_gusts_10m'
        ],
        'timezone': 'auto'
    }

    try:
        # Make the API request
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the JSON response
        data = response.json()

        return data

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None


def interpret_weather_code(weather_code):
    """
    Interpret the WMO weather code into human-readable description
    """
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }

    return weather_codes.get(weather_code, "Unknown weather code")


def display_weather_info(weather_data, location_name=""):
    """
    Display weather information in a readable format
    """
    if not weather_data or 'current' not in weather_data:
        print("No weather data available")
        return

    current = weather_data['current']
    print(current)

    print("\n" + "=" * 50)
    if location_name:
        print(f"WEATHER FORECAST - {location_name.upper()}")
    else:
        print("CURRENT WEATHER")
    print("=" * 50)

    # Time information
    current_time = datetime.fromisoformat(current['time'].replace('Z', '+00:00'))
    print(f"Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Temperature information
    print(f"Temperature: {current['temperature_2m']}°{current['units']['temperature_2m']}")
    print(f"Feels like: {current['apparent_temperature']}°{current['units']['apparent_temperature']}")

    # Weather conditions
    weather_desc = interpret_weather_code(current['weather_code'])
    print(f"Weather: {weather_desc}")
    print(f"Cloud Cover: {current['cloud_cover']}{current['units']['cloud_cover']}")

    # Day/Night information
    is_day = "Day" if current['is_day'] else "Night"
    print(f"Time of Day: {is_day}")

    # Precipitation
    print(f"Precipitation: {current['precipitation']} {current['units']['precipitation']}")
    if current.get('rain', 0) > 0:
        print(f"Rain: {current['rain']} {current['units']['rain']}")
    if current.get('snowfall', 0) > 0:
        print(f"Snowfall: {current['snowfall']} {current['units']['snowfall']}")

    # Wind information
    print(f"Wind Speed: {current['wind_speed_10m']} {current['units']['wind_speed_10m']}")
    print(f"Wind Direction: {current['wind_direction_10m']}°")
    if current.get('wind_gusts_10m'):
        print(f"Wind Gusts: {current['wind_gusts_10m']} {current['units']['wind_gusts_10m']}")

    # Pressure and humidity
    print(f"Pressure: {current['pressure_msl']} {current['units']['pressure_msl']}")
    print(f"Humidity: {current['relative_humidity_2m']}{current['units']['relative_humidity_2m']}")

    print("=" * 50)


def main():
    """
    Main function to demonstrate the weather API
    """
    # Example locations (latitude, longitude, name)
    locations = [
        (40.7128, -74.0060, "New York City"),
        (51.5074, -0.1278, "London"),
        (35.6762, 139.6503, "Tokyo"),
        (48.8566, 2.3522, "Paris"),
    ]

    print("Open-Meteo Current Weather Demo")
    print("Fetching current weather for major cities...")

    for lat, lon, name in locations:
        print(f"\nFetching weather for {name}...")
        weather_data = get_current_weather(lat, lon)

        if weather_data:
            display_weather_info(weather_data, name)
        else:
            print(f"Failed to get weather data for {name}")

        # Add a small delay between requests to be respectful to the API
        import time
        time.sleep(1)


# Alternative: Get weather for custom location
def get_custom_location_weather():
    """
    Get weather for a custom location entered by user
    """
    try:
        lat = float(input("Enter latitude: "))
        lon = float(input("Enter longitude: "))
        location_name = input("Enter location name (optional): ")

        weather_data = get_current_weather(lat, lon)
        if weather_data:
            display_weather_info(weather_data, location_name)
        else:
            print("Failed to get weather data")

    except ValueError:
        print("Please enter valid numeric coordinates")


if __name__ == "__main__":
    # Run the main demo
    main()

    # Uncomment the line below to try custom location input
    # get_custom_location_weather()