from mini_web import route, render_template, Response

@route("/")
def home(request):
    return render_template(request, "home.html")

@route("/about")
def about(request):
    return render_template(request, "about.html")

