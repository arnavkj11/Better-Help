import re
from datetime import datetime as dt

from models.appointments import Appointment

def create_new_appointment(form_data):
    """
        Returns the appointment object or raises validation error!
    """
    therapist_id = form_data.get('therapist_id')
    patient_id = form_data.get('patient_id')
    datetime = form_data.get('appointment_datetime')
    type_ = form_data.get('appointment_type')
    location = form_data.get('location')
    online_link = form_data.get('online_link')
    notes = form_data.get('notes')

    # validation
    if not therapist_id:
        raise Exception("Field `therapist_id` is required!")
    if not patient_id:
        raise Exception("Field `patient_id` is required!")
    if not datetime:
        raise Exception("Field `appointment_datetime` is required!")
    if not type_:
        raise Exception("Field `appointment_type` is required!")
    if type_ not in ('online', 'in-person'):
        raise Exception("Invalid appointment type. It should be `online` or `in-person`!")
    if type_ == 'online' and not online_link:
        raise Exception("Field `online_link` is required!")
    if type_ == 'in-person' and not location:
        raise Exception("Field `location` is required!")
    # validate link regex
    link_pattern = re.compile(r'^(http|https|ftp)://[^\s/$.?#].[^\s]*$')
    if online_link and not link_pattern.match(online_link):
        raise Exception("Field `online_link` should be a valid link!")
    # validate datetime, should be greater than current datetime
    if dt.strptime(datetime, "%Y-%m-%dT%H:%M") < dt.now():
        raise Exception("Field `appointment_datetime` should be greater than current datetime!")

    if isinstance(datetime, str):
        datetime = dt.strptime(datetime, "%Y-%m-%dT%H:%M")
    appointment, _ = Appointment.get_or_create_appointment(patient_id, therapist_id, datetime, notes, type_, location, online_link)
    return appointment


def get_appointments(patient_id=None, therapist_id=None):
    """
        Returns the list of appointments for the given patient or therapist.
    """
    appointments = Appointment.select()
    
    if patient_id:
        appointments = appointments.where(Appointment.patient_id == patient_id)
    if therapist_id:
        appointments = appointments.where(Appointment.therapist_id == therapist_id)
    
    return appointments