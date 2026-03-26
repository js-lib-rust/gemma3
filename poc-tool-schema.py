from transformers.utils import get_json_schema
import json


def get_current_weather(location: str, unit: str = "Celsius") -> dict:
    """
    Gets the current weather in a given location.

    Args:
        location: The city and state, e.g. "San Francisco, CA" or "Tokyo, JP"
        unit: The unit to return the temperature in. (choices: ["Celsius", "Fahrenheit"])

    Returns:
        temperature: The current temperature in the given location
        weather: The current weather in the given location
    """
    return {"temperature": 15, "weather": "sunny"}


function_definition = get_json_schema(get_current_weather)
print(json.dumps(function_definition, indent=2, ensure_ascii=False))
