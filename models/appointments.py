from peewee import ForeignKeyField, TextField, DateTimeField, CharField

from models.users import User, BaseModel

class Appointment(BaseModel):
    patient = ForeignKeyField(User, backref='appointments')
    therapist = ForeignKeyField(User, backref='appointments_as_therapist')
    appointment_datetime = DateTimeField()
    notes = TextField(null=True)
    appointment_type = CharField(choices=["online", "in-person"], default="in-person")
    location = CharField(null=True)
    online_link = CharField(null=True)

    def get_dict(self) -> dict:
        return {
            "id": self.id,
            "patient_id": self.patient.id,
            "therapist_id": self.therapist.id,
            "appointment_datetime": self.appointment_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "notes": self.notes,
            "appointment_type": self.appointment_type,
            "location": self.location,
            "online_link": self.online_link,
        }

    @classmethod
    def get_or_create_appointment(cls, patient, therapist, appointment_datetime, notes=None, appointment_type="in-person", location=None, online_link=None):
        appointment, created = cls.get_or_create(
            patient=patient,
            therapist=therapist,
            appointment_datetime=appointment_datetime,
            notes=notes,
            appointment_type=appointment_type,
            location=location,
            online_link=online_link
        )
        return appointment, created