# Licensed Materials - Property of IBM
# 5725I71-CC011829
# (C) Copyright IBM Corp. 2015, 2020. All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.

from flask import Blueprint, render_template, current_app, send_from_directory
from qpylib import qpylib

import json
import os
import html

import get_data

# pylint: disable=invalid-name
viewsbp = Blueprint('viewsbp', __name__, url_prefix='/')
app = viewsbp


def pass_data(objects):
    json_string = json.dumps(objects)
    return json_string


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


@app.route('/test/func')
def test_func():
    message = {'greeting': 'Hello from Flask!'}
    return json.dumps(message)


@viewsbp.route('/get/all')
def get_all():
    return pass_data(get_data.get_all())


@viewsbp.route('/get/routers')
def get_routers():
    return pass_data(get_data.get_routers())


@viewsbp.route('/get/raw/<routerid>')
def get_raw(routerid=None):
    return pass_data(get_data.get_raw(routerid))


@viewsbp.route('/get/timeline/<routerid>')
def get_timeline(routerid=None):
    return pass_data(get_data.get_timeline(routerid))


@viewsbp.route('/get/mock')
def mock_get():
    data = '[ { "name": "Testing MikroTik",' \
           '"networks": [], "offenses": [], "devices": [] },' \
           '{ "name": "Testing MikroTik (Direct)",' \
           '"networks": ["192.168.88.1"],' \
           '"offenses": [],' \
           '"devices": [ { "mac": "08:00:27:01:27:15", "ip": [ "192.168.88.244" ] } ] } ]'
    return data


@viewsbp.route('/test/api')
def test_api_call():
    response = qpylib.REST('GET', '/api/help/versions', params={'Range': 'items=0-49'}, verify=False)
    return json.dumps(response.json())


@viewsbp.route('/test/import')
def test_imports():
    import objects
    return json.dumps(objects.init_device())


@viewsbp.route('/playground')
def playground():
    to_see = ''
    # to_see += str(os.environ) + '\n'
    to_see += json.dumps(get_data.get_raw(162), indent=2)

    to_see = html.escape(to_see).replace('\n', '<br>')
    return to_see
