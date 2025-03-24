from datetime import datetime

from models.users import User, PatientProfile, TherapistProfile

def process_signup_form(form_data: dict):
    """
        Returns the user object or raises validation error!
    """
    name = form_data.get('name')
    email = form_data.get('email')
    password1 = form_data.get('password1')
    password2 = form_data.get('password2')
    role = form_data.get('role')

    # validation
    if password1 != password2:
        raise Exception("Passwords do not match!")
    if role not in ['patient', 'therapist']:
        raise Exception("Invalid role!")
    if role == 'patient':
        is_patient = True
    else:
        is_patient = False
    user, created = User.get_or_create_user(name, email, password1, is_patient)
    if not created:
        raise Exception("User already exists!")
    return user

def process_login_form(form_data: dict):
    email = form_data.get('email')
    password = form_data.get('password')

    user = User.get_user_by_email(email)
    if not user:
        raise Exception("User does not exist!")
    if user.password != password:
        raise Exception("Invalid password!")
    return user

def get_therapists(q: str = None) -> list:
    """
        Returns the list of therapists.

        Args:
            q (str): Search query
        Returns:
            list: List of therapists, i.e. list of dicts
    """
    if q:
        query = User.filter_therapists_by_name(q)
    else:
        query = User.get_all_therapists()
    therapists = []
    for therapist in query:
        therapists.append(therapist.get_dict())
    return therapists

def get_therapist_by_id(therapist_id: int) -> dict:
    """
        Returns the therapist object.

        Args:
            therapist_id (int): Therapist id
        Returns:
            dict: Therapist object
    """
    therapist = User.get_therapist_by_id(therapist_id)
    return therapist

def process_profile_form(form_data: dict, files: dict = None, current_user: User = None):
    user_id = form_data.pop('user_id')
    if not user_id:
        raise Exception("Invalid user id!")
    user = User.get_by_id(user_id)
    if not user:
        raise Exception("User does not exist!")
    if current_user and user.id != current_user.id:
        raise Exception("Invalid user id!")
    # convert dob to date object if it is a string
    dob = form_data.get('dob')
    if dob:
        if isinstance(dob, str):
            form_data['dob'] = datetime.strptime(dob, "%Y-%m-%d").date()
    # check gender value
    gender = form_data.get('gender')
    if gender == "":
        gender = None
    if gender:
        assert gender in ('Male', 'Female', 'Other', ), 'gender does not match! it should be Male, Female or Other'
    # handle profile photo
    photo = files.get('photo')
    photo_changed = form_data.pop('patient_photo_changed', None) or form_data.pop('therapist_photo_changed', None)
    if photo_changed is not None and photo_changed == 'true':
        if photo:
            photo_file_path = f"static/images/profile_user_{user.id}.{photo['filename'].split('.')[-1]}"
            with open(photo_file_path, "wb") as f:
                f.write(photo['file'])
        else:
            photo_file_path = "static/images/profile_default.jpg"
        form_data['photo'] = "/" + photo_file_path
    else:
        form_data['photo'] = user.profile.photo
    if user.is_patient:
        profile, created = PatientProfile.get_or_create_profile(user)
        profile = PatientProfile.update_profile(profile, **form_data)
    else:
        profile, created = TherapistProfile.get_or_create_profile(user)
        profile = TherapistProfile.update_profile(profile, **form_data)
    profile.save()
    return profile
