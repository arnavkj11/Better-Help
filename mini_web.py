"""
This is a mini web framework for defining abstractions
    that make it easier to develop web applications without repeating code.
Here is the design of the mini web framework:

- Routing: Introduce a way to easily define routes
    and associate them with functions (views).
- Template Rendering: Allow dynamic generation of HTML
    by replacing placeholders.
- Request and Response Abstraction: Create classes that encapsulate
    request data and response generation.
- Middleware: Allow functions to run before processing
    the main request, useful for tasks like logging or authentication.
"""

import os
import json
from http.server import SimpleHTTPRequestHandler, HTTPServer
from http import cookies
from functools import wraps

from utils import parse_form_data, parse_form_data_with_files, parse_query_params

STATIC_DIR = os.path.join(os.getcwd(), "static")


# Request and Response Abstraction


class Request:
    def __init__(self, method, path, query_params=None, form_data=None, files=None):
        self.method = method
        self.path = path
        self.form_data = form_data or {}
        self.files = files or {}
        self.query_params = query_params or {}
        self.cookies = cookies.SimpleCookie()
        self.user = None


class Response:
    def __init__(self, content=b"", status=200, content_type="text/html"):
        self.content = content
        self.status = status
        self.content_type = content_type

class JSONResponse(Response):
    def __init__(self, content=dict(), status=200):
        content_json = json.dumps(content)
        super().__init__(content=content_json.encode(), status=status, content_type="application/json")


# Routing
ROUTES = {}

def route(path):
    def wrapper(fn):
        ROUTES[path] = fn
        return fn
    return wrapper

# Middleware
MIDDLEWARES = []

def middleware(fn):
    MIDDLEWARES.append(fn)
    print("Added middleware: ", fn)
    return fn

# Custom Decorators
def login_required(fn):
    @wraps(fn)
    def decorated_view(request, *args, **kwargs):
        if request.user is not None:
            return fn(request, *args, **kwargs)
        else:
            if "/api" in request.path:
                return JSONResponse(content={"message": "Unauthorized access. Please log in."}, status=401)
            # TODO Redirect to the login page or any other action for unauthorized users
            return Response(content=b"Unauthorized access. Please log in. <a href='/login'>login here</a>", status=401)

    return decorated_view

def patient_required(fn):
    @wraps(fn)
    def decorated_view(request, *args, **kwargs):
        if request.user is not None and request.user.is_patient:
            return fn(request, *args, **kwargs)
        else:
            if "/api" in request.path:
                return JSONResponse(content={"message": "Unauthorized access. Patients only."}, status=401)
            # TODO Redirect to a page or take any other action for unauthorized users
            return Response(content=b"Unauthorized access. Patients only. <a href='/logout'>logout here</a>", status=401)

    return decorated_view

def therapist_required(fn):
    @wraps(fn)
    def decorated_view(request, *args, **kwargs):
        if request.user is not None and request.user.is_therapist:
            return fn(request, *args, **kwargs)
        else:
            if "/api" in request.path:
                return JSONResponse(content={"message": "Unauthorized access. Therapists only."}, status=401)
            # TODO Redirect to a page or take any other action for unauthorized users
            return Response(content=b"Unauthorized access. Therapists only.", status=401)

    return decorated_view


# Template Rendering, TODO: Add support for jinja2
from jinja2 import Environment, FileSystemLoader
template_env = Environment(loader=FileSystemLoader('templates'))

def render_template(request, template_name, context={}) -> Response:
    """
        Renders the template with the given context and returns a response object.
    """
    template = template_env.get_template(template_name)
    context.update({"user": request.user})
    content = template.render(context)
    return Response(content=bytes(content, 'utf-8'), content_type="text/html")

# Simple Session
import uuid

SESSIONS = {}

def create_session(user_instance):
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = user_instance
    return session_id

def get_user_from_session(session_id):
    return SESSIONS.get(session_id)

def delete_session(session_id):
    if session_id in SESSIONS:
        del SESSIONS[session_id]

# Static Files
def get_content_type(file_path):
    if file_path.endswith(".html"):
        return "text/html"
    elif file_path.endswith(".css"):
        return "text/css"
    elif file_path.endswith(".js"):
        return "application/javascript"
    elif file_path.endswith(".png"):
        return "image/png"
    elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
        return "image/jpeg"
    else:
        return "application/octet-stream"  # Default to binary stream

def serve_static_file(path):
    file_path = os.path.join(STATIC_DIR, path.replace("/static/", "", 1))
    
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            content = f.read()
            # Depending on the file extension, set the appropriate content type
            content_type = get_content_type(file_path)
            return Response(content=content, content_type=content_type)

    return Response(status=404, content=b"File not found!")

# Database
from peewee import SqliteDatabase, Model as DBModel
db = SqliteDatabase('database.db')

class BaseModel(DBModel):
    class Meta:
        database = db

# Main Handler
class FrameworkHandler(SimpleHTTPRequestHandler):
    def handle_request(self, method):
        form_data = {}
        files = {}
        content_type = self.headers.get('Content-type', '')
        length = int(self.headers.get('Content-length', 0))
        if method == "POST" and 'multipart/form-data' in content_type:
            # parse form data
            form_data, files = parse_form_data_with_files(self.rfile, content_type, max_length=length)
        elif method == "POST":
            data = self.rfile.read(length).decode()
            form_data = parse_form_data(data)
        # parse url
        url_path, query_params = parse_query_params(self.path)
        # Create the request object
        request = Request(method=method, path=url_path, query_params=query_params, form_data=form_data, files=files)
        # Incoming cookies
        incoming_cookies = cookies.SimpleCookie(self.headers.get("Cookie"))
        request.cookies = incoming_cookies

        # Check if the user is authenticated
        session_id = request.cookies.get('session_id')
        if session_id:
            session_id = session_id.value
            user_instance = get_user_from_session(session_id)
            if user_instance:
                request.user = user_instance

        # Run middleware
        response = None
        for middleware_fn in MIDDLEWARES:
            response = middleware_fn(request)
            if response:  # If any middleware returns a response, break out and return that response.
                break

        if not response:
            # Serve static files
            if request.path.startswith("/static/"):
                response = serve_static_file(request.path)
            else:
                # Existing code for handling routes
                response = ROUTES.get(request.path, self.default_response)(request)

        self.send_response(response.status)
        self.send_header('Content-type', response.content_type)
        self.end_headers()
        self.wfile.write(response.content)

    def default_response(self, request):
        return Response(content=b"Page not found", status=404, content_type="text/plain")

    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")


# Server Initialization
def run():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, FrameworkHandler)
    print("Server started at http://localhost:8000/")
    httpd.serve_forever()
