def hera_list_devices():
    """
    List all devices registered to HERA.
    """


def hera_describe_device(device: str):
    """
    Create a detailed description of the requested device.

    Args:
        device: device name is a required string parameter; if is missing do not invoke any function but return error message.
    """


def hera_get_device_actions(device: str):
    """
    Retrieves the actions supported by a device.

    Args:
        device: device name is a required string parameter; if is missing do not invoke any function but return error message.
    """


def hera_read_temperature(zone: str):
    """
    Retrieves the current temperature reading from a specified zone within the home. If zone name parameter is not present into user prompt, use living room as default.

    Args:
        zone: is the location where the devices are placed; if you cannot determine the zone from user prompt use living room as default value.
    """


def hera_read_humidity():
    """
    Read current humidity.
    """


def hera_read_sensors():
    """
    Read all registered sensors.
    """


def hera_start_heating():
    """
    Start central heating.
    """


def hera_stop_heating():
    """
    Stop central heating.
    """


def hera_get_heating_state():
    """
    Get central heating state.
    """


def hera_run_diagnose(device: str):
    """
    Check that a device is running properly and is reacheable and return a diagnose report.

    Args:
        device: device name is a required string parameter; if is missing do not invoke any function but return error message.
    """
