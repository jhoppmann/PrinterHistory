from logging import Logger

from flask import Flask, request, Response
import json
import logging
from mysql_connection import Connector
from statistics_calculator import StatisticsCalculator
from datetime import datetime
from sys import exit


def setup_logger() -> 'Logger':
    """Sets up a file logger for the application"""
    log = logging.getLogger('phistory')
    log.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('phistory.log')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)
    return log


log = setup_logger()

log.info('Starting up Print History application')
app = Flask(__name__)

log.info('Loading config.json...')
try:
    fp = open('config.json', 'r')
    config = json.load(fp)
except FileNotFoundError:
    log.error('Error while loading config (file not found). Exiting app.')
    exit(1)
except json.decoder.JSONDecodeError:
    log.error('config.json doesn\'t contain valid JSON. Exiting app.')
    exit(1)
else:
    log.info("config.json found and loaded")

connector = Connector(config['dbconfig'], log)
webhook_key = ''
if 'webhook_key' in config:
    webhook_key = config['webhook_key']
calculator = StatisticsCalculator(connector)


@app.route("/webhook", methods=['POST'])
def webhook() -> str:
    """This method is the webhook endpoint"""
    log.info('Request received')
    if webhook_key != '':
        try:
            api_secret = request.form['apiSecret']
            if api_secret != webhook_key:
                return Response('{"status": "failure", "reason": "Api key is wrong!."}',
                                status=401, mimetype='application/json')
        except KeyError as argh:
            log.error("Api Key missing")
            return Response('{"status": "failure", "reason": "Api key missing in request."}',
                            status=400, mimetype='application/json')
    try:
        topic = request.form['topic']
        if topic == 'Print Done' or topic == 'Print Failed':
            handle_finish(request)
        else:
            log.info("Nothing to save, discarding data.")
        return "success"
    except KeyError as argh:
        log.error("Key missing from data" + str(request))
        return Response('{"status": "failure", "reason": "Key missing in request."}',
                        status=400, mimetype='application/json')


def handle_finish(req: 'flask_request') -> None:
    """Extracts and handles data from a print success request."""
    data = extract_info(req)
    connector.save(**data)


@app.route("/data", methods=['GET'])
def get_data() -> str:
    """Returns all entries from database as JSON"""
    data = connector.load_data()
    print(data)
    for line in data:
        line['DATE'] = datetime.timestamp(line['DATE'])
    log.info("All data fetched, returning " + str(len(data)) + " lines")
    return json.dumps(data)


def extract_info(req: 'flask_request') -> dict:
    data = {}
    extras = json.loads(req.form['extra'])
    data['file'] = extras['name']
    data['time'] = extras['time']
    data['topic'] = req.form['topic']
    data['machine'] = req.form['deviceIdentifier']
    log.info('New data: ' + str(data))
    return data


if __name__ == '__main__':
    app.run(host='0.0.0.0')
