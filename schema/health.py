# Save blood pressure measurement of 124/88 mmHg and heart rate of 75 bpm for Rotaru Iulian.
def health_save_blood_measurement(person: str, systole: int, diastole: int, pulse: int):
    """
    Save person blood pressure and cardiac pulse in the medical database. Also compute pulse pressure as difference between systolic and diastolic pressures.

    Args:
        person: human-readable person name, unique per medical database.
        systole: systolic pressure expressed as mmHg (millimeters of mercury).
        diastole: diastolic pressure expressed as mmHg (millimeters of mercury).
        pulse: heart rate expressed in bpm (beats per minute).
    """


# Save body temperature of 35.10 °C for Lontkowschi George.
def health_save_temperature(person: str, temperature: float):
    """
    Save person body temperature in the medical database.

    Args:
        person: human-readable person name, unique per medical database.
        temperature: body temperature expressed in °C (Celsius degrees)
    """


# Save body weight of 89.50 kg and height of 176 cm for Păduraru Mihaela.
def health_save_weight(person: str, weight: float, height: int):
    """
    Save person body weight in the medical database. Also compute body mass index based on person height.

    Args:
        person: human-readable person name, unique per medical database.
        weight: body weight expressed in kg (kilogram).
        height: person height expressed in cm (centimeters).
    """


# Save blood glucose level of 80 mg/dL for Dorneanu Sorana Ioana.
def health_save_glucose(person: str, glucose: int):
    """
    Save person blood glucose level in the medical database.

    Args:
        person: human-readable person name, unique per medical database.
        glucose: blood glucose level expressed in mg/dL (milligrams per deciliter).
    """


# Read medical records from 2026-01-22 for Gogălniceanu Ștefan.
def health_read_medical_records(person: str, date: str):
    """
    Read person records from the medical database for a specified date.

    Args:
        person: human-readable person name, unique per medical database.
        date: the past date we want to retrieve the medical records, in ISO 8601 format, e.g. 2026-03-24
    """
