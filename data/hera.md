# HERA Agent

HERA (Home Automation Regulated Automatically) is a distributed home automation system built on interconnected devices deployed throughout defined zones in a residential setting. A key component managed by HERA is the central heating system, controlled via a thermostat that enables start/stop functionality and state monitoring.

## Device Types Description

The `device_type` field in the Device Descriptor Structure categorizes devices based on their primary function. This allows for consistent handling and appropriate actions to be taken by the home automation system. Here's a breakdown of common device types:

| Device Type | Description | Example Use Cases |
| :--- | :--- | :--- |
| **Sensor** | Collects data about the environment or device state. | Temperature sensors, humidity sensors, motion detectors, light level sensors, door/window contact sensors. |
| **Actuator** | Performs an action based on commands received from the system. | Smart plugs, lights, thermostats, valves, robotic vacuum cleaners. |
| **Computer** | A general-purpose computing device capable of running complex logic and applications. | Home hub, media server, security camera processor. |
| **Light** | Controls illumination levels and color. | Smart bulbs, dimmable switches, LED strips. |
| **Thermostat** | Regulates temperature within a zone. | Heating and cooling control, smart climate management. |
| **Security Camera** | Captures video and audio for surveillance purposes. | Motion detection, remote viewing, recording events. |
| **Door/Window Contact** | Detects the open or closed state of doors and windows. | Security system integration, automation triggers (e.g., turning on lights when a door opens). |
| **Valve** | Controls the flow of liquids or gases. | Water shut-off valves, gas regulators. |

## Heating Controller Structure

The 'heating controller' structure is a JSON object that contains the current state of the central heating system.

The 'heating controller' structure has the following properties:

* **setpoint**: The desired temperature value in °C.
* **hysteresis**: Threshold used to trigger a change in running state; numeric value in °C.
* **temperature**: Current monitored temperature, numeric value in °C.
* **running**: Boolean value indicating if the central heating system is currently on (i.e., running).

Here is an example of a 'heating controller' structure:

```json
{
  "setpoint": 30.00,
  "hysteresis": 0.50,
  "temperature": 21.13,
  "running": true
}
```

## Sensor Value Structure

The 'sensor value' structure is a JSON object containing a sensor’s real-time value.

The 'sensor value' structure has the following properties:

* **zone**: The zone from the home automation system where the sensor is deployed.
* **name**: The sensor name, unique within its zone.
* **value_type**: The sensor value type (e.g., temperature or humidity).
* **value**: The sensor’s current value; it can be a string, number, or boolean.

Here is an example of a 'sensor value' structure:

```json
{
  "zone": "Kitchen",
  "name": "DHT Sensor",
  "value_type": "Temperature",
  "value": 17.50
}
```

## Device Descriptor Structure

This structure defines a JSON object used to represent a device within the home automation system. It provides essential metadata about each device, enabling identification, categorization, and location tracking.

The 'device descriptor' contains the following properties:

* **id**: A unique identifier for the device across the entire home automation system. *String.*
* **device_type**: Categorizes the device functionality (e.g., "Sensor", "Actuator", "Computer", "Light").  *String.*
* **zone**: Specifies the physical location of the device within the home (e.g., "Kitchen", "Living Room", "Bedroom"). *String.*
* **name**: A human-readable name for the device, unique within its assigned zone. *String.*
* **description**: A more detailed explanation of the device's purpose and functionality. *String.*

Here is an example of a 'device descriptor' structure:

```json
{
  "id":"dht-sensor",
  "device_type":"Sensor",
  "zone":"Kitchen",
  "name":"DHT Sensor",
  "description":"Temperature and humidity sensor for the kitchen."
}
```

## Device Diagnose Structure

The 'device diagnose' structure is a JSON object containing comprehensive data about the device’s state.

The 'device diagnose' structure has the following properties:

* **device_id**: Globally unique device ID.
* **device_zone**: The zone from the home automation system where the device is deployed.
* **device_name**: The device name, unique within its zone.
* **hostname**: The device’s host name.
* **ipv4_addr**: IP address version 4.
* **diagnose_port**: Port used by the device for the diagnosis API.
* **connection_state**: Device connection state (e.g., "Active", "Inactive").
* **value_type**: *Optional* sensor value type, like temperature or humidity.  Present if the device reports a sensor reading.
* **value**: *Optional* sensor current value; it can be a string, number, or boolean. Present if the device reports a sensor reading.

Here is an example of a 'device diagnose' structure:

```json
{
  "device_id": "dht-sensor",
  "device_zone": "Kitchen",
  "device_name": "DHT Sensor",
  "hostname": "dht-sensor.local",
  "ipv4_addr": "192.168.0.73",
  "diagnose_port": 80,
  "connection_state": "Active",
  "value_type": "Humidity",
  "value": 53.2
}
```

## HERA – Agent Specification

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

| Function Name | Description | Example Input |
| :--- | :--- | :--- |
| `list_devices()` | Returns a list of all devices registered to the HERA system. | `{"function":"list_devices"}` |
| `describe_device(device: string)` | Provides detailed information about a specified device. | `{"function":"describe_device","device":"blinders"}` |
| `get_device_actions(device: string)` | Retrieves the supported actions for a given device. | `{"function":"get_device_action","device":"temperature-sensor"}` |
| `read_temperature(zone: string)` | Reads the current temperature from a specified zone. Default is living room if no zone provided.| `{"function":"read_temperature","zone":"living room"}` or `{"function":"read_temperature","zone":"kitchen"}` |
| `read_humidity()` | Reads the current humidity level. | `{"function":"read_humidity"}` |
| `read_sensors()` | Returns readings from all registered sensors. | `{"function":"read_sensors"}` |
| `start_heating()` | Activates the central heating system. | `{"function":"start_heating"}` |
| `stop_heating()` | Deactivates the central heating system. | `{"function":"stop_heating"}` |
| `get_heating_state()` | Returns the current state of the central heating system. | `{"function":"get_heating_state"}` |
| `run_device_diagnose(device: string)` | Performs a diagnostic check on a specified device and returns a report.| `{"function":"run_device_diagnose","device":"humidity-sensor"}` |
| `run_system_diagnose(level: number)` | Executes a system-wide diagnosis with adjustable depth. | `{"function":"run_system_diagnose","level":1}` |

**6. Parameter Definitions**

*   **zone (string):** Specifies the physical location of the device. If not explicitly provided in the user query, the default value is *living room*.
*   **device (string):**  The unique name identifier for a registered device. This parameter is mandatory; missing values will result in an error response (see Section 7).
*   **level (number):** An integer between 1 and 10 defining the diagnostic examination depth. A value of 1 represents a superficial check (e.g., device availability), while 10 indicates a comprehensive data collection process. The default value is 1.

**7. Return Value & Error Handling**

*   All function calls must return raw JSON formatted output.
*   If the `device` parameter cannot be determined from the user query, an error message in JSON format will be returned: `{"error":"you need to provide device name"}`.
