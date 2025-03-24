import traceback

from mini_web import route, render_template, Response, JSONResponse, middleware, get_user_from_session, create_session, delete_session, login_required

from controllers.users import process_signup_form, process_login_form, get_therapists, process_profile_form, get_therapist_by_id
from controllers.appointments import get_appointments

@route("/signup")
def signup_view(request):
    return render_template(request, "signup.html")

@route("/api/signup")
def signup_api(request):
    """
    Process the signup form and create a new user if not exists.
    """
    if not request.method == "POST":
        response = {
            "message": "Method not allowed"
        }
        return JSONResponse(content=response, status=405)
    try:
        user = process_signup_form(request.form_data)
        return JSONResponse(content=user.get_dict(), status=201)
    except Exception as e:
        response = {
            "message": str(e)
        }
        return JSONResponse(content=response, status=400)


@route("/login")
def login_view(request):
    return render_template(request, "login.html")

@route("/api/login")
def login_api(request):
    """
    Process the login form and create a new session.
    """
    if not request.method == "POST":
        response = {
            "message": "Method not allowed"
        }
        return JSONResponse(content=response, status=405)
    try:
        user = process_login_form(request.form_data)
        # create session and redirect to dashboard
        session_id = create_session(user)
        return JSONResponse(content={"session_id": session_id}, status=200)
    except Exception as e:
        response = {
            "message": str(e)
        }
        return JSONResponse(content=response, status=400)


@route("/logout")
def logout_view(request):
    session_id = request.cookies.get('session_id').value
    delete_session(session_id)
    return render_template(request, "login.html")

@route("/api/logout")
def logout_api(request):
    """
    Delete the session.
    """
    if not request.method == "POST":
        response = {
            "message": "Method not allowed"
        }
        return JSONResponse(content=response, status=405)
    try:
        session_id = request.cookies.get('session_id')
        if session_id:
            session_id = session_id.value
            delete_session(session_id)
            return JSONResponse(content={"message": "Logged out successfully!"}, status=200)
        else:
            return JSONResponse(content={"message": "Already logged out!"}, status=200)
    except Exception as e:
        response = {
            "message": str(e)
        }
        return JSONResponse(content=response, status=400)

@route("/search")
def search_therapist_view(request):
    """
    Search for therapists based on the search query.
    """
    return render_template(request, "therapists.html")

@route("/api/search")
def search_therapist_api(request):
    """
    Search for therapists based on the search query in JSON format.
    """
    q = request.query_params.get("q")
    therapists = get_therapists(q)
    return JSONResponse(content=therapists)

@route("/therapists")
def therapists_view(request):
    """
    Get all therapists.
    """
    therapist_id = request.query_params.get("id", None)
    if therapist_id:
        therapist = get_therapist_by_id(therapist_id)
        if therapist is None:
            return Response(content=b"Page not found", status=404, content_type="text/plain")
        return render_template(request, "therapist.html")
    return render_template(request, "therapists.html")

@route("/api/therapists")
def therapists_api(request):
    """
    Get all therapists in JSON format.
    """
    therapists = get_therapists()
    therapist_id = request.query_params.get("id", None)
    if therapist_id:
        therapist = get_therapist_by_id(therapist_id)
        if therapist is None:
            response = {
                "message": "Therapist not found"
            }
            return JSONResponse(content=response, status=404)
        response = therapist.get_dict()
        number_of_appointments = len(get_appointments(therapist_id=therapist_id))
        response["number_of_appointments"] = number_of_appointments
        return JSONResponse(content=response)
    return JSONResponse(content=therapists)

@route("/profile")
@login_required
def profile_view(request):
    """
    Get user profile.
    """
    return render_template(request, "profile.html", context={})

@route("/api/profile")
@login_required
def profile_api(request):
    """
    Get/edit user profile in JSON format.
    """
    user = request.user

    if request.method == "GET":
        profile = user.profile
        return JSONResponse(content=profile.get_dict())
    elif request.method == "POST":
        try:
            profile = process_profile_form(request.form_data, request.files, current_user=user)
            return JSONResponse(content=profile.get_dict())
        except Exception as e:
            traceback.print_exc()
            response = {
                "message": str(e)
            }
            return JSONResponse(content=response, status=400)
    else:
        response = {
            "message": "Method not allowed"
        }
        return JSONResponse(content=response, status=405)

@route("/profile/edit")
@login_required
def profile_edit_view(request):
    """
    Edit user profile.
    """
    return render_template(request, "profile_edit.html", context={})

@route("/api/user")
@login_required
def user_api(request):
    """
    Get user details in JSON format.
    """
    user = request.user
    return JSONResponse(content=user.get_dict())
