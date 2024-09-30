from flask import Flask, render_template, abort, request, send_from_directory
from typing import Optional
from jinja2.exceptions import TemplateNotFound
from werkzeug.exceptions import NotFound as WerkzeugNotFound

from pyflex import exceptions as pyflex_exceptions
from . import services


app = Flask(
    "SpiUI",
    template_folder="webui/html/",
    static_folder="webui/resources/",
)


app.jinja_options = {
    'block_start_string': '[%',
    'block_end_string': '%]',
    'variable_start_string': '[[',
    'variable_end_string': ']]',
    'comment_start_string': '[#',
    'comment_end_string': '#]'
}


def file_to_url(path: str) -> Optional[str]:
    return f"/outputs/{path}" if path else None


@app.route("/api/flashrom", methods=["POST"])
def flashrom():

    service = services.get_flashrom()

    action = request.form.get("action")
    programmer = request.form.get("programmer")
    file = request.files.get("file-upload")
    file_data = file.read() if file else None

    service.set_action(action)
    service.set_programmer(programmer)

    if file_data:
        service.set_file(file_data)

    if "force" in request.form:
        service.set_force()

    if "very-very-verbose" in request.form:
        service.set_verbosity(3)

    try:
        result = service.execute()

    except pyflex_exceptions.PyFlexInvalidParameter as ex:
        return str(ex), 400

    except pyflex_exceptions.PyFlexException as ex:
        return str(ex), 500

    else:
        return {
            "msg": result.message,
            "out": file_to_url(result.path)
        }


@app.route("/outputs/<file>")
def get_output(file) -> str:
    try:
        return send_from_directory('webui/outputs', file)

    except WerkzeugNotFound as ex:
        abort(404)


@app.route("/")
@app.route("/<page>")
def get_index(page: str = 'home') -> str:
    try:
        return render_template(
            "layout.html",
            Page=page,
            PageTitle=page.title())

    except TemplateNotFound:
        abort(404)

