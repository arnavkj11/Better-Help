from .users import User, PatientProfile, TherapistProfile
from .appointments import Appointment
from mini_web import db

db.connect()
db.create_tables([User, PatientProfile, TherapistProfile, Appointment], safe=True)

# Every user should have a profile
for user in User.select():
    if user.is_patient:
        PatientProfile.get_or_create_profile(user)
    else:
        TherapistProfile.get_or_create_profile(user)
print("Created tables successfully!")
