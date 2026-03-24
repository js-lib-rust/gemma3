def health_save_blood(person: str, systole: int, diastole: int, pulse: int):
    """
    Save person blood pressure and cardiac pulse to medical database. Also compute pulse pressure as difference between systolic and diastolic pressures.

    Args:
        person: human-readable person name, unique per medical database.
        systole: systolic pressure expressed as mmHg (millimeters of mercury).
        diastole: diastolic pressure expressed as mmHg (millimeters of mercury).
        pulse: heart rate expressed in bpm (beats per minute).
    """


def health_save_temperature(person: str, temperature: float):
    """
    Save person body temperature to medical database.

    Args:
        person: human-readable person name, unique per medical database.
        temperature: body temperature expressed in °C (Celsius degrees)
    """


def health_save_weight(person: str, height: int, weight: float):
    """
    Save person body weight to medical database. Also compute body mass index based on person height.

    Args:
        person: human-readable person name, unique per medical database.
        height: person height expressed in cm (centimeters).
        weight: body weight expressed in kg (kilogram).
    """


def health_save_glucose(person: str, glucose: int):
    """
    Save person blood glucose level to medical database.

    Args:
        person: human-readable person name, unique per medical database.
        glucose: blood glucose level expressed in mg/dL (milligrams per deciliter).
    """


def health_read_measurements(person: str, date: str):
    """
    Read person medical records for a specified past date -- there is no reason to provide dates from the future.

    Args:
        person: human-readable person name, unique per medical database.
        date: the past date we want to retrieve the medical records, in ISO 8601 format, e.g. 2026-03-24
    """
