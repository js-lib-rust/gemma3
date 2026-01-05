# Weather Agent

This agent provides real-time weather information and forecasts for a specified location. It retrieves data to deliver current conditions, daily outlooks, and hourly predictions, supporting outdoor activities and preparedness. The agent outputs weather data in structured JSON format, designed for easy parsing and integration with various applications.

## Current Weather Structure

The 'current weather' structure is a JSON object containing real-time weather information observed over a 15-minute interval.

This structure has the following properties:

* **weather**: A short description of the current weather status (e.g., "Mainly clear", "Light rain"). String value.
* **temperature**: The current temperature, expressed as a numeric value in degrees Celsius (°C).
* **wind**: The current wind speed, expressed as a numeric value in kilometers per hour (km/h).
* **precipitation**: The probability of precipitation occurring within the interval, expressed as a percentage (%).

Here is an example of a 'current weather' object:

```json
{
  "weather":"Mainly clear",
  "temperature":-1.2,
  "wind":14.7,
  "precipitation":0.0
}
```

## Daily Forecast Structure

The 'daily forecast' structure is a JSON object containing weather information for a single day. Function responses typically include multiple daily forecasts, formatted in JSONL (JSON Lines) format. These structures are designed to be displayed in a tabular layout.

This structure has the following properties:

* **date**: The date for which the forecast applies, represented as a string with the YYYY-MM-DD format.
* **weather**: A short description of the expected weather status for the day (e.g., "Slight snow showers", "Partly cloudy"). String value.
* **temperature_max**: The estimated maximum temperature for the day, expressed as a numeric value in degrees Celsius (°C).
* **temperature_min**: The estimated minimum temperature for the day, expressed as a numeric value in degrees Celsius (°C).
* **precipitation**: The maximum probability of precipitation occurring during the day, expressed as a percentage (%).
* **wind**: The estimated maximum wind speed for the day, expressed as a numeric value in kilometers per hour (km/h).

Here is an example of a daily forecast object:

```json
{
  "date":"2025-12-31",
  "weather_code":"Slight snow showers",
  "temperature_max":-0.6,
  "temperature_min":-3.3,
  "precipitation":48,
  "wind":22.4
}
```

## Hourly Forecast Structure

The hourly forecast structure is a JSON object containing weather information for a single hour interval. Function responses typically include multiple hourly forecasts, formatted in JSONL (JSON Lines) format. These structures are designed to be displayed in a tabular layout.

This structure has the following properties:

* **time**: The hour for which the forecast applies, represented as a string with the HH:MM format.
* **weather**: A short description of the expected weather status during that hour (e.g., "Overcast", "Light drizzle"). String value.
* **temperature**: The estimated average temperature for the hour, expressed as a numeric value in degrees Celsius (°C).
* **precipitation**: The maximum probability of precipitation occurring during the hour, expressed as a percentage (%).
* **wind**: The estimated maximum wind speed for the hour, expressed as a numeric value in kilometers per hour (km/h).

Here is an example of an hourly forecast object:

```json
{
  "time":"2025-12-22 00:00",
  "weather":"Overcast",
  "temperature":2.3,
  "precipitation":0,
  "wind":3.7
}
```

## Displaying Hints

Usually the current weather structure is formatted as a single phrase, with weather parameters in natural order.

Here is an example of a formatted current weather phrase:
```text
The weather is currently mainly clear. The temperature is -1.2°C, with a wind speed of 14.7 km/h and no precipitation.
```

The other two structures are displayed as tables.

**Daily Forecast Table Example:**

| Date | Weather | Max Temp (°C) | Min Temp (°C) | Precipitation (%) | Wind (km/h) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2025-12-31 | Slight snow showers | -0.6 | -3.3 | 48 | 22.4 |
| ... | ... | ... | ... | ... | ... |

**Hourly Forecast Table Example:**

| Time | Weather | Temperature (°C) | Precipitation (%) | Wind (km/h) |
| :--- | :--- | :--- | :--- | :--- |
| 00:00 | Overcast | 2.3 | 0 | 3.7 |
| 01:00 | Overcast | 2.1 | 0 | 4.1 |
| 02:00 | Light rain | 1.8 | 15 | 5.3 |
| ... | ... | ... | ... | ... |

## How is weather 'date' parameter displayed?
The weather 'date' parameter is displayed as 'Date'. It is only the day part, formatted as YYYY-MM-DD.

## How is weather 'time' parameter displayed?
The weather 'time' parameter is displayed as 'Time'. It is only the time part, formatted as HH:MM.

## How is 'weather' parameter displayed?
The 'weather' parameter is displayed as 'Weather'.

## How is the weather 'temperature' parameter displayed?
The 'temperature' parameter is displayed as 'Temperature (°C)'.

## How is the weather 'precipitation' parameter displayed?
The 'precipitation' parameter is displayed as 'Precipitation (%)'.

## How is the weather 'wind' parameter displayed?
The 'wind' parameter is displayed as 'Wind (km/h)'.
