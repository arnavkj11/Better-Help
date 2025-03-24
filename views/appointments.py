import traceback

from mini_web import route, render_template, Response, JSONResponse, middleware, login_required, patient_required

from controllers.users import get_therapist_by_id
from controllers.appointments import create_new_appointment


@route("/schedule_appointment")
@patient_required
@login_required
def schedule_appointment_view(request):
    return render_template(request, "schedule_appointment.html")

@route("/api/schedule_appointment")
@login_required
@patient_required
def schedule_appointment_api(request):
    if not request.method == "POST":
        return JSONResponse(content={"message": "Method not allowed"}, status=405)
    try:
        form_data = request.form_data
        appointment = create_new_appointment(form_data)
        return JSONResponse(content=appointment.get_dict(), status=200)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(content={"message": str(e)}, status=400)
