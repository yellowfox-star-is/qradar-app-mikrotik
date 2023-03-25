# Licensed Materials - Property of IBM
# 5725I71-CC011829
# (C) Copyright IBM Corp. 2015, 2020. All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.

from flask import Blueprint, render_template, current_app, send_from_directory
from qpylib import qpylib

import json
import os

from . import get_data

# pylint: disable=invalid-name
viewsbp = Blueprint('viewsbp', __name__, url_prefix='/')
app = viewsbp


# A simple "Hello" endpoint that demonstrates use of render_template
# and qpylib logging.
@viewsbp.route('/')
@viewsbp.route('/<name>')
def hello(name=None):
    qpylib.log('name={0}'.format(name), level='INFO')
    return render_template('hello.html', name=name)


# The presence of this endpoint avoids a Flask error being logged when a browser
# makes a favicon.ico request. It demonstrates use of send_from_directory
# and current_app.
@viewsbp.route('/favicon.ico')
def favicon():
    return send_from_directory(current_app.static_folder, 'favicon-16x16.png')


@viewsbp.route('/monitor')
def monitor():
    return render_template('monitor.html')


@app.route('/test_func')
def test_func():
    message = {'greeting':'Hello from Flask!'}
    return json.dumps(message)


@viewsbp.route('/get_all')
def get_all():
    data = get_data.get_all()
    return json.dumps(data, indent=2)


@viewsbp.route('/mock_get')
def get_all():
    data = get_data.get_all()
    return json.dumps(data, indent=2)


@viewsbp.route('/test_api')
def test_api_call():
    response = qpylib.REST('GET', '/api/help/versions', params={'Range': 'items=0-49'})
    return response


@viewsbp.route('/playground')
def playground():
    to_see = ''
    # to_see += str(os.environ) + '\n'
    to_see += os.environ['CURL_CA_BUNDLE'] + '<br>'
    to_see += os.environ['REQUESTS_CA_BUNDLE']
    return to_see
