def weather_get_current_weather(locality: str):
    """
    Get current weather data for a locality.

    Args:
        locality: the name of the locality for which weather data will be retrieved.
    """


def weather_get_today_forecast(locality: str):
    """
    Get the hourly weather forecast for today in the requested location.

    Args:
        locality: the name of the locality for which the hourly weather forecast will be retrieved.
    """


def weather_get_forecast(locality: str, days: int):
    """
    Get the daily weather forecast for the next few days in the requested location.

    Args:
        locality: the name of the locality for which the daily weather forecast will be retrieved.
        days: the number of days we want the forecast for, starting from the current date, not included.
    """
