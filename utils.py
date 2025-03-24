# TODO: move utility function from mini_web.py to utils.py
import cgi, json
from urllib.parse import parse_qs, urlparse

def parse_form_data(data) -> dict:
    form_data = parse_qs(data)
    if form_data == {}:
        try:
            form_data = json.loads(data)
        except:
            pass
    for k,v in form_data.items():
        if isinstance(v, list) and len(v) == 1:
            form_data[k] = v[0]
        if not isinstance(v, list):
            form_data[k] = v
    return form_data

def parse_form_data_with_files(file, content_type, max_length=0):
    form = cgi.FieldStorage(
        fp=file,
        headers={'content-type': content_type, 'content-length': max_length},
        environ={'REQUEST_METHOD': 'POST'}
    )
    form_data = {}
    files = {}
    for field in form.keys():
        field_item = form[field]
        if field_item.filename:
            files[field] = {
                'filename': field_item.filename,
                'content_type': field_item.type,
                'file': field_item.file.read()
            }
        else:
            form_data[field] = field_item.value
    return form_data, files

def parse_query_params(url) -> tuple:
    parsed_url = urlparse(url)
    query_params = parse_form_data(parsed_url.query)
    return parsed_url.path, query_params