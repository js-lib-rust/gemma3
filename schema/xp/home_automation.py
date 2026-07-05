# Read the temperature sensor in the living room.
def home_automation_read_sensor_value(sensor_name: str, zone_name: str = None):
    """
    Read the value of the named sensor, optionally specifying the zone in which the sensor is located.

    Args:
        sensor_name: the human-readable name of the sensor.
        zone_name: the name of the zone where the sensor is located, optional.
    """


def home_automation_execute_action(action_name: str, device_name: str, zone_name: str = None):
    """
    Execute action on named device, optionally specifying the zone in which the device is located.

    Args:
        action_name: action to be executed on device.
        device_name: the human-readable name of the device.
        zone_name: the name of the zone where the device is located, optional.
    """


# Set the brightness level to 50% for light actuator in the bedroom.
# Set the color to red for light actuator in the bedroom.
def home_automation_set_property(physical_property: str, value: str, device_name: str, zone_name: str = None):
    """
    Set the physical property value to the named device, optionally specifying the zone in which the device is located.

    Args:
        physical_property: physical property to set.
        value: new value for the physical property.
        device_name: the human-readable name of the device.
        zone_name: the name of the zone where device is located, optional.
    """


# Get the brightness level of the light actuator in the bedroom.
# Get the color of the light actuator in the bedroom.
def home_automation_get_property(physical_property: str, device_name: str, zone_name: str = None):
    """
    Get the value of a physical property of the named device, optionally specifying the zone in which the device is located.

    Args:
        physical_property: physical property for which the value is obtained.
        device_name: the human-readable name of the device.
        zone_name: the name of the zone where device is located, optional.
    """


def home_automation_get_device_status(device_name: str, zone_name: str = None):
    """
    Get the internal status of the named device, optionally specifying the zone in which the device is located.

    Args:
        device_name: the human-readable name of the device.
        zone_name: the name of the zone where device is located, optional.
    """
