import sys
import traceback
from flask import (
    Flask,
    jsonify,
    render_template,
    request
)
from parser import parse_string
from util import to_json, type_name
from visitor import NodeVisitor

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/parse', methods=['POST'])
def parse():
    source = request.form.get('source', "")
    if not source.endswith("\n"):
        source += "\n"
    return jsonify(tree=to_json(parse_string(source)))


@app.route('/transform', methods=['POST'])
def transform():
    source = request.form.get('source', "")
    if not source.endswith("\n"):
        source += "\n"
    node = parse_string(source)

    visitor_source = request.form.get('visitor', "")
    globals_ = {
        "NodeVisitor": NodeVisitor,
        "type_name": type_name
    }
    output = None
    error = None
    try:
        exec(visitor_source, globals_, None)
        visitor = globals_["Visitor"]()
        visitor.visit(node)
        output = str(node)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        parts = traceback.extract_tb(exc_traceback)
        _, lineno, _, _ = parts[-1]
        error = {
            "lineno": lineno,
            "message": str(exc_value)
        }

    return jsonify(output=output, error=error)


if __name__ == "__main__":
    app.run()
