from flask import Flask, request
import logging

server = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True

@server.route('/', methods=['POST'])
def listener():
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(data['log'])
        except:
            pass
        return 'ok'

"""
to run this madness
$ export FLASK_APP=event_catcher.py
$ python3 -m flask run --port=6070 --host=0.0.0.0
"""