from flask import Flask
from threading import Thread

# app = Flask(__name__)

# import logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask('')


@app.route('/')
def home():
  return "Alive and Running"


def run():
  app.run(host='0.0.0.0', port=8080)


def keepalive():
  t = Thread(target=run)
  t.start()
