# Save blood pressure measurement of 124/88 mmHg and heart rate of 75 bpm for Rotaru Iulian.
from dataclasses import dataclass
from typing import List

from pydantic import BaseModel, Field


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
        date: the date we want to retrieve the medical records, in ISO 8601 format, e.g. 2026-03-24
    """

@dataclass
class MedicalRecord:
    """
    Represents a single medical measurement.

    Args:
        timestamp: moment when record was created, in format YYYY-MM-DD HH:MM:SS.
        person: human-readable person name, unique per medical database.
        measurement: measurement type.
        value: measurement numeric value.
    """

    timestamp: str
    person: str
    measurement: str
    value: float


def health_evaluate_medical_records(records: List[MedicalRecord]):
    """
    Evaluate medical records. Returns given records list with 'resolution' field updated.

    Args:
        records: A list of objects containing timestamp (ISO 8601), person name,
                 the type of measurement (e.g., 'Heart Rate'), and the numeric value.
                 Resolution field is not defined on input.
    """
    pass


def health_compute_body_mass_index(weight: float, height: float):
    """
    Computer body mass index for given weight and height.

    Args:
        weight: person weight expressed in kg ((kilograms).
        height: person height expressed in cm (centimeters).
    """
