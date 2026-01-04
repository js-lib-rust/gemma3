# Question Answering Agent
We have here multiple agents ...

## MEDICAL AGENT
It is about my health measurement ...

### What heart measurements are typically taken?
Here are the types of heart, also known as cardiac, measurements:

* **Systolic Pressure** is the top number in a blood pressure reading, representing the pressure in your arteries when
  your heart beats and pushes blood out; it is measured in mmHg
* **Diastolic Pressure** is the lower number in a blood pressure reading, measuring the pressure in your arteries when
  your heart rests and refills with blood between beats; it is measured in mmHg
* **Pulse Pressure (PP)** is the simple difference between your systolic (top) and diastolic (bottom) blood pressure
  numbers, representing the force your heart generates with each beat; it is measured in mmHg
* **Heart Rate**, also known as **Pulse**, is the number of times your heart beats per minute (bpm) and it reflects how
  hard your heart is working to pump blood; it is measured in bpm

## What is blood pressure?
Blood pressure is the force of your blood pushing against your artery walls as your heart pumps it through your body.

## What is normal value for systolic blood pressure?
A normal systolic blood pressure (the top number) for adults is less than 120 mmHg. Readings between 120-129 systolic
are considered elevated, while 130 or higher starts to indicate high blood pressure (hypertension).

## What is normal value for diastolic blood pressure?
A normal diastolic blood pressure (the bottom number) for adults is less than 80 mmHg, with the ideal being below 80
mmHg. Readings of 80-89 mmHg indicate elevated or Stage 1 hypertension, requiring attention, while 90 mmHg or higher
signifies Stage 2 hypertension.

## What is normal value for pulse pressure?
Pulse pressure (PP) is typically around 40 mmHg in healthy adults. While a normal pulse pressure indicates healthy
artery flexibility, a wide (high) or narrow (low) reading can signal underlying issues like stiff arteries or low blood
volume.

## What is normal value for heart rate?
A normal resting heart rate for adults is typically between 60 and 100 bpm, but it varies with activity, fitness, age,
emotions.

## What blood measurements are typically taken?
Here are the types of blood measurements:

* **Glucose Level**, also known as **Blood Sugar**, measures the amount of sugar (glucose) in your blood, which is your
  body's main source of energy; it is measured in mg/dL
* **Oxygen Saturation Level (SpO2)** measures the percentage of hemoglobin in your blood carrying oxygen, showing how
  well oxygen travels from your lungs to the rest of your body; it is expressed as percent (%)

## What is normal value for glucose level?
Normal blood glucose levels are generally below 100 mg/dL when fasting, and below 140 mg/dL two hours after a meal.

## What is normal value for oxygen saturation level?
A normal blood oxygen saturation (SpO2) for a healthy person is 95% to 100%.

## What body measurements are typically taken?
Here are the types of body measurements:

* **Body Height** is the measurement of a person's vertical size, taken while standing erect on a flat surface; it is
  measured in cm
* **Body Weight** is the total mass of your body, a combination of muscle, bone, fat, water, and organs; it is measured
  in kg
* **Body Mass Index (BMI)** is a screening tool that uses your height and weight to estimate body fat; it is scalar
  value without measurement unit
* **Body Temperature** is a measure of the body's internal heat, a crucial indicator of health and metabolic function;
  it is measured in °C

## How body mass index is classified?
BMI Categories (Adults)

* **Underweight**: below 18.5
* **Normal Weight**: 18.5 – 24.9
* **Overweight**: 25.0 – 29.9
* **Obese**: 30.0 or higher

## What is normal range for body temperature?
While 37°C is a classic average for body temperature, a normal range for adults is generally considered 36.1°C to
37.2°C, with fluctuations common.

## What neural measurements are typically taken?
Here is the neural measurement, currently a single type:

* **Intelligence Quotient (IQ)** is a standardized score from tests measuring cognitive abilities like reasoning,
  problem-solving, and memory; it is a scalar value without measurement unit

## What is normal range for IQ?
Average intelligence quotient (IQ) is generally defined as a score between 90 and 109, with the statistical average set
at 100. This range encompasses the majority of the population.

## What is a health measurement structure?
The 'health measurement' structure is a JSON object that contains measurement type an its numeric value. There can be
one or multiple structures in a function response, in JSONL format. Health measurements are stored in the medical
database.

It has next properties:

* **timestamp**: date string with format YYYY-MM-DD HH:MM:SS
* **person**: person name owning the measurement, string
* **measurement**: health measurement type, string
* **value**: measurement value, numeric

Here is an example of a health measurement structure:

```json
{
  "timestamp": "2025-12-17 08:47:02",
  "person": "Iulian Rotaru",
  "measurement": "systolic_pressure",
  "value": 124
}
```

## How is body_temperature parameter displayed?
Parameter body_temperature is displayed as 'Body Temperature'. It is measured in celsius degrees (°C).

## What is the function parameter for 'Body Temperature'?
The function parameter for 'Body Temperature' is body_temperature.

## How is body_weight parameter displayed?
Parameter body_weight is displayed as 'Body Weight'. It is measured in kilograms (kg).

## What is the function parameter for 'Body Weight'?
The function parameter for 'Body Weight' is body_weight.

## How is body_height parameter displayed?
Parameter body_height is displayed as 'Body Height'. It is measured in centimeters (cm).

## What is the function parameter for 'Body Height'?
The function parameter for 'Body Height' is body_height.

## How is body_max_index parameter displayed?
Parameter body_max_index is displayed as 'Body Mass Index (BMI)'. It is a scalar value and has no measurement units.

## What is the function parameter for 'Body Mass Index (BMI)'?
The function parameter for 'Body Mass Index (BMI)' is body_max_index.

## How is systolic_pressure parameter displayed?
Parameter systolic_pressure is displayed as 'Systolic Pressure'. It is a measured in millimeters of mercury (mmHg).

## What is the function parameter for 'Systolic Pressure'?
The function parameter for 'Systolic Pressure' is systolic_pressure.

## How is diastolic_pressure parameter displayed?

Parameter diastolic_pressure is displayed as 'Diastolic Pressure'. It is a measured in millimeters of mercury (mmHg).
## What is the function parameter for 'Diastolic Pressure'?

The function parameter for 'Diastolic Pressure' is diastolic_pressure.
## How is pulse_pressure parameter displayed?

Parameter pulse_pressure is displayed as 'Pulse Pressure'. It is a measured in millimeters of mercury (mmHg).
## What is the function parameter for 'Pulse Pressure'?

The function parameter for 'Pulse Pressure' is pulse_pressure.
## How is heart_rate parameter displayed?

Parameter heart_rate is displayed as 'Heart Rate'. It is a measured in millimeters of mercury (mmHg).
## What is the function parameter for 'Heart Rate'?
The function parameter for 'Heart Rate' is heart_rate.

## How is glucose_level parameter displayed?
Parameter glucose_level is displayed as 'Glucose Level' or 'Blood Sugar'. Is is measured in milligrams per deciliter (
mg/dL).

## What is the function parameter for 'Glucose Level'?
The function parameter for 'Glucose Level' is glucose_level.

## What is the function parameter for 'Blood Sugar'?
The function parameter for 'Blood Sugar' is glucose_level.

## How is oxygen_saturation parameter displayed?
Parameter oxygen_saturation is displayed as 'Oxygen Saturation Level (SpO2)'. It is expressed as percent.

## What is the function parameter for 'Oxygen Saturation Level (SpO2)'?
The function parameter for 'Oxygen Saturation Level (SpO2)' is oxygen_saturation.

## What does spo2 stand for?
The acronym spo2 stand for Oxygen Saturation Level. It is a blood related measurement.

## What means spo2?
SpO2 means oxygen saturation, representing the percentage of oxygen-carrying hemoglobin in your blood.

## What is the acronym for Oxygen Saturation Level?
The acronym for Oxygen Saturation Level is SpO2.

## How is intelligence_quotient parameter displayed?
Parameter intelligence_quotient is displayed as 'Intelligence QuotientIndex (IQ)'. It is a scalar value without
measurement units.

## What is the function parameter for 'Intelligence QuotientIndex (IQ)'?
The function parameter for 'Intelligence QuotientIndex (IQ)' is intelligence_quotient.

## HERA Home Automation System – Agent Specification

**1. Introduction**

HERA (Home Automation Regulated Automatically) is a distributed home automation system comprised of interconnected devices deployed across defined zones within a residential environment. This document details the functionality and operational characteristics of the HERA agent, responsible for managing device interaction and responding to user requests.

**2. System Architecture & Components**

The HERA architecture centers around a network of *devices* categorized into two primary functional types: *sensors* and *actuators*. 

*   **Sensors:** These devices collect quantitative measurements representing physical properties within the home environment. Currently, implemented sensor capabilities include temperature and humidity detection.
*   **Actuators (Controllers):** Actuators execute actions to modify the state of controllable systems. The current implementation features a single actuator dedicated to controlling the central heating system, designated as 'thermostat'.

The system is currently configured with two zones: *living room* and *kitchen*. The kitchen zone contains both the 'thermostat' actuator (directly interfacing with the apartment’s heating infrastructure) and a DHT sensor module providing temperature and humidity readings. The living room zone incorporates a dedicated temperature sensor, labeled ‘thermostat sensor’, utilized by the 'thermostat' actuator for feedback control.

**3. Agent Communication & Control Interface**

The HERA agent communicates directly with deployed devices via HTTP REST API calls.  The agent maintains an internal registry of available devices and provides programmatic access through a defined function call interface. Access permissions are differentiated based on device type: 

*   **Sensors:** The agent is limited to *read-only* operations for sensors, retrieving measurement data.
*   **Actuators:** The agent supports both *start* and *stop* functions for actuators, enabling control of connected systems.  The agent also provides management functions for device administration.

**4. Agent Functional Requirements**

The HERA agent is responsible for the following core functionalities:

*   **Query Analysis & Function Invocation:** Parse user queries to identify the requested action and invoke the corresponding function within the system’s API.
*   **Parameter Extraction:**  Identify and extract necessary parameters from the user query required by the target function. If parameter extraction fails, no function call is initiated (see Section 7). The term 'indoor' is synonymous with the home environment.
*   **Function Execution & Data Handling:** Execute the appropriate home automation function with extracted parameters.
*   **Error Handling:**  Generate and return informative error messages in JSON format when required parameters are missing or invalid.

**5. Available Functions (API)**

The following functions are currently supported by the HERA agent:

| Function Name                            | Description                                                        | Example Input                      |
|:-----------------------------------------|--------------------------------------------------------------------|-------------------------------------|
| `list_devices()`                         | Returns a list of all devices registered to the HERA system.       | `{"function":"list_devices"}`         |
| `describe_device(device: string)`        | Provides detailed information about a specified device.          | `{"function":"describe_device","device":"blinders"}` |
| `get_device_actions(device: string)`     | Retrieves the supported actions for a given device.            | `{"function":"get_device_action","device":"temperature-sensor"}` |
| `read_temperature(zone: string)`         | Reads the current temperature from a specified zone. Default is living room if no zone provided.| `{"function":"read_temperature","zone":"living room"}` or `{"function":"read_temperature","zone":"kitchen"}` |
| `read_humidity()`                        | Reads the current humidity level.                                  | `{"function":"read_humidity"}`         |
| `read_sensors()`                         | Returns readings from all registered sensors.                       | `{"function":"read_sensors"}`         |
| `start_heating()`                        | Activates the central heating system.                              | `{"function":"start_heating"}`        |
| `stop_heating()`                         | Deactivates the central heating system.                             | `{"function":"stop_heating"}`        |
| `get_heating_state()`                    | Returns the current state of the central heating system.           | `{"function":"get_heating_state"}`    |
| `run_device_diagnose(device: string)`    | Performs a diagnostic check on a specified device and returns a report.| `{"function":"run_device_diagnose","device":"humidity-sensor"}` |
| `run_system_diagnose(level: number)`     | Executes a system-wide diagnosis with adjustable depth.        | `{"function":"run_system_diagnose","level":1}` |

**6. Parameter Definitions**

*   **zone (string):** Specifies the physical location of the device. If not explicitly provided in the user query, the default value is *living room*.
*   **device (string):**  The unique name identifier for a registered device. This parameter is mandatory; missing values will result in an error response (see Section 7).
*   **level (number):** An integer between 1 and 10 defining the diagnostic examination depth. A value of 1 represents a superficial check (e.g., device availability), while 10 indicates a comprehensive data collection process. The default value is 1.

**7. Return Value & Error Handling**

*   All function calls must return raw JSON formatted output.
*   If the `device` parameter cannot be determined from the user query, an error message in JSON format will be returned:  `{"error":"you need to provide device name"}`.

## What is an 'heating controller' structure?
The 'heating controller' structure is a JSON object that contains current status of the heating system.

The 'heating controller' structure has next properties:
* **setpoint**: the desired temperature value in °C 
* **hysteresis**: threshold used when trigger a change in running state; numeric value in °C
* **temperature**: current monitored temperature, numeric value in °C
* **running**: boolean value indicating if the heating system is currently on, aka running  

Here is an example of an 'heating controller' object:
```json
{
  "setpoint":30.00,
  "hysteresis":0.00,
  "temperature":21.13,
  "running":true
}
```

## What is a 'sensor value' structure?
The 'sensor value' structure is a JSON object containing a sensor real-time value.

The 'sensor value' structure has next properties:
* **zone**: zone from home automation system where sensor is deployed 
* **name**: sensor name, unique in its zone
* **value_type**: sensor value type, like temperature or humidity
* **value**: sensor current value; it has mixed type: can be string, number or boolean

Here is an example of a 'sensor value' object:
```json
{
  "zone":"Kitchen",
  "name":"DHT Sensor",
  "value_type":"Temperature",
  "value":17.50
}
```

## What is a 'device diagnose' structure?
The 'device diagnose' structure is a JSON object containing a comprehensive data about device state.

The 'device diagnose' structure has next properties:
* **device_id**: globally unique device ID 
* **device_zone**: zone from home automation system where device is deployed 
* **device_name**: device name, unique in its zone
* **hostname**: device host name
* **ipv4_addr**: IP address version 4 
* **diagnose_port**: port used by device for diagnose API
* **connection_state**: device connection state
* **value_type**: optional sensor value type, like temperature or humidity
* **value**: optional sensor current value; it has mixed type: can be string, number or boolean

Here is an example of a 'device diagnose' object:
```json
{
  "device_id":"dht-sensor",
  "device_zone":"Kitchen",
  "device_name":"DHT Sensor",
  "hostname":"dht-sensor.local",
  "ipv4_addr":"192.168.0.73",
  "diagnose_port":80,
  "connection_state":"Active",
  "value_type":"Humidity",
  "value":13.5
}
```

# WEATHER AGENT

## What is a 'current weather' structure?
The 'current weather' structure is a JSON object containing real-time weather information observed for 15 minutes
interval.

The 'current weather' structure has next properties:
* **weather**: short description of the perceived weather status
* **temperature**: current temperature, numeric value (°C)
* **wind**: current wind speed, numeric value (km/h)  
* **precipitation**: precipitation probability expressed as percent (%)  

Here is an example of a 'current weather' object:
```json
{
  "weather":"Mainly clear",
  "temperature":-1.2,
  "wind":14.7,
  "precipitation":0.0
}
```

## How is current weather displayed?
Usually current weather structure is formatted as a single phrase, with weather parameters in natural order.

Here is an example of formated current weather phrase:
The weather is currently mainly clear. The temperature is -1.2°C, with a wind speed of 14.7 km/h and no precipitation.

## What is a 'daily forecast' structure?
The 'daily forecast' structure is a JSON object that contains weather information for a day. There are usually multiple
structures in a function response, in JSONL format. Daily forecast structures are always displayed in a table format.

The 'daily forecast' structure has the following properties mapped to the table column:
* **date**: Date: day for which forecast is computed, string with format YYYY-MM-DD
* **weather**: Weather: short description of the perceived weather status
* **temperature_max**: Max Temp (°C): estimated maximum temperature, numeric value in Celsius degrees
* **temperature_min**: Min Temp (°C): estimated minimum temperature, numeric value in Celsius degrees
* **precipitation**: Precipitation (%): maximum precipitation probability expressed as percent
* **wind**: Wind (km/h): estimated maximum wind speed, numeric value in kilometers per hour

Here is an example of a daily forecast structure:
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

## What is a hourly forecast structure?
The hourly forecast structure is a JSON object that contains weather information about an hour interval. There are
usually multiple structures in a function response, in JSONL format. Hourly forecast structures are always displayed in
table format.

The hourly forecast structure has next properties mapped on table column:
* **time**: Time: hour for which forecast is computed, string with format HH:MM
* **weather**: Weather: short description of the perceived weather status
* **temperature**: Temperature (°C): estimated average temperature, numeric value in Celsius degrees
* **precipitation**: Precipitation (%): maximum precipitation probability expressed as percent
* **wind**: Wind (km/h): estimated maximum wind speed, numeric value in kilometers per hour

Here is an example of a hourly forecast structure:
```json
{
  "time":"2025-12-22 00:00",
  "weather":"Overcast",
  "temperature":2.3,
  "precipitation":0,
  "wind":3.7
}
```

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
