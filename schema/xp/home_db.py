# home-db:List the temperature sensors in the house.
# home-db:List all the devices in the kitchen.
def home_db_list_devices(device_type: str, zone_name: str = None):
    """
    List all devices of a certain type or 'all' keyword for any type, optionally specifying the zone where the devices are located.

    Args:
        device_type: the human-readable device type or 'all' for any type.
        zone_name: the name of the zone where devices are located, optional.
    """


# home-db:Get the description of the light actuator in the kitchen.
def home_db_get_device_description(device_name: str, zone_name: str = None):
    """
    Get the technical description of the named device, optionally specifying the zone in which the device is located.

    Args:
        device_name: the human-readable name of the device.
        zone_name: the name of the zone where device is located, optional.
    """
