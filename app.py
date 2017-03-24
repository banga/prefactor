from flask import (
    Flask,
    jsonify,
    render_template,
    request
)
from parser import parse_string
from util import to_json

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
