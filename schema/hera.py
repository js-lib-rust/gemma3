def hera_list_devices():
    """
    List all devices registered to HERA.
    """


def hera_describe_device(device: str):
    """
    Create a detailed description of the requested device.

    Args:
        device: human-readable device name, unique per HERA.
    """


def hera_get_device_actions(device: str):
    """
    Retrieves the actions supported by a device.

    Args:
        device: human-readable device name, unique per HERA.
    """


def hera_read_temperature(zone: str):
    """
    Read the current temperature from devices in a specified zone.

    Args:
        zone: human-readable zone name of the location where the devices are placed.
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
    Check that a device is reachable and running properly. Return a diagnosis report.

    Args:
        device: human-readable device name, unique per HERA.
    """
