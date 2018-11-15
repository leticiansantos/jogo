import logging
from datetime import datetime, timedelta

import requests
from chalice import Chalice, Response

app = Chalice(app_name='concierge-api')
app.debug = True
app.log.setLevel(logging.DEBUG)

from chalicelib.db.models import SampleModel


@app.route('/')
def index():
    response = requests.get('http://httpbin.org/ip')
    return response.json()

@app.route('/hi')
def index():
    response = requests.get('http://httpbin.org/ip')
    return {
        'hello':'world'
    }
