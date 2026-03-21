from transformers.utils import get_json_schema
import json
import schema

def get_current_weather(location: str, unit: str = "celsius"):
    """
    Gets the current weather in a given location.

    Args:
        location: The city and state, e.g. "San Francisco, CA" or "Tokyo, JP"
        unit: The unit to return the temperature in. (choices: ["celsius", "fahrenheit"])

    Returns:
        temperature: The current temperature in the given location
        weather: The current weather in the given location
    """
    return {"temperature": 15, "weather": "sunny"}


print(json.dumps(schema.get("home_automation")))

function_definition = get_json_schema(get_current_weather)
print(json.dumps(function_definition))
