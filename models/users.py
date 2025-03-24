import datetime

from peewee import *

from mini_web import BaseModel

class User(BaseModel):
    name = CharField(null=True)
    email = CharField(unique=True)
    password = CharField(null=True)
    is_patient = BooleanField(default=True)

    created_at = DateTimeField(default=datetime.datetime.now)

    def get_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_patient": self.is_patient,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "profile": self.profile.get_dict()
        }

    @property
    def is_therapist(self):
        return not self.is_patient
    
    @staticmethod
    def get_or_create_user(name, email, password, is_patient=True):
        user, created = User.get_or_create(name=name, email=email, is_patient=is_patient)
        if not created:
            return user, created
        user.password = password
        user.save()
        return user, created
    
    @staticmethod
    def get_user_by_email(email):
        try:
            return User.get(User.email == email)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def get_all_therapists():
        return User.select().where(User.is_patient == False)
    
    @staticmethod
    def get_therapist_by_id(therapist_id):
        try:
            return User.select().where(User.is_patient == False, User.id == therapist_id).get()
        except User.DoesNotExist:
            return None

    @staticmethod
    def filter_therapists_by_name(query: str):
        return User.select().where(User.is_patient == False, User.name.contains(query))
    
    @property
    def profile(self):
        try:
            if self.is_patient:
                profile, _ = PatientProfile.get_or_create_profile(self)
            else:
                profile, _ = TherapistProfile.get_or_create_profile(self)
            return profile
        except Profile.DoesNotExist:
            print("ERROR: Profile does not exist!")
            return None

class Profile(BaseModel):
    user = ForeignKeyField(User, unique=True)
    dob = DateField(null=True)
    gender = CharField(null=True)
    contact_info = CharField(null=True)
    photo = CharField(default="/static/images/profile_default.jpg") # path to photo

    def get_dict(self) -> dict:
        return {
            'user_id': self.user_id,
            'dob': self.dob.strftime('%Y-%m-%d') if self.dob else None,
            'gender': self.gender,
            'contact_info': self.contact_info,
            'photo': self.photo
        }

    @classmethod
    def get_or_create_profile(cls, user: User):
        profile, created = cls.get_or_create(user=user)
        return profile, created
    
    @staticmethod
    def update_profile(profile, **kwargs):
        for key, value in kwargs.items():
            setattr(profile, key, value)
        profile.save()
        return profile

class PatientProfile(Profile):
    emergency_contact_info = CharField(null=True)
    medical_history = CharField(null=True)
    insurance_info = CharField(null=True)

    def get_dict(self) -> dict:
        profile_dict = super().get_dict()
        profile_dict.update({
            "emergency_contact_info": self.emergency_contact_info,
            "medical_history": self.medical_history,
            "insurance_info": self.insurance_info
        })
        return profile_dict

class TherapistProfile(Profile):
    office_address = CharField(null=True) # for in-person meetings
    meeting_link = CharField(null=True) # for online meetings
    license_info = CharField(null=True)
    speciality = CharField(null=True)
    experience = DecimalField(max_digits=3, decimal_places=1, null=True) # in years
    bio = CharField(null=True)

    def get_dict(self) -> dict:
        profile_dict = super().get_dict()
        profile_dict.update({
            "office_address": self.office_address,
            "meeting_link": self.meeting_link,
            "license_info": self.license_info,
            "speciality": self.speciality,
            "experience": float(self.experience) if self.experience else None,
            "bio": self.bio
        })
        return profile_dict
