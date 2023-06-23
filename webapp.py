from logging import Logger

from flask import Flask, request, Response
from flask_cors import CORS, cross_origin

import json
import logging

from mail_sender import MailSender
from mysql_connection import Connector
from statistics_calculator import StatisticsCalculator
from json_rpc_handler import JsonRpcHandler
from datetime import datetime
from sys import exit


def register_rpc_methods(calculator: StatisticsCalculator, handler: JsonRpcHandler):
    methods = {'PRINT_TIME': calculator.print_time,
               'NUMBERS_BY_PRINTERS': calculator.numbers_by_printers,
               'NUMBERS_BY_PRINTERS_CLEANED': calculator.numbers_by_printers_cleaned,
               'MEAN_PRINT_LENGTH': calculator.mean_print_length,
               'PRINTS_BY_MONTH_AND_PRINTER': calculator.prints_by_month_and_printer,
               'ALL_DATA': calculator.all_data,
               'FAIL_RATE_BY_PRINTERS': calculator.fail_rate_by_printers,
               'CUMULATIVE_PRINTS': calculator.cumulative_prints}
    handler.register("CALCULATOR", methods)
    pass


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


# setup code
log = setup_logger()

log.info('Starting up Print History application')
app = Flask(__name__)
CORS(app)

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
mail_sender = None
if 'mailconfig' in config:
    mail_sender = MailSender(config['mailconfig'], log)
webhook_key = ''
if 'webhook_key' in config:
    webhook_key = config['webhook_key']
json_rpc_handler = JsonRpcHandler()
register_rpc_methods(StatisticsCalculator(connector), json_rpc_handler)


@app.route("/webhook", methods=['POST'])
def webhook() -> Response:
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
        return Response('{"status": "success"}', status=200, mimetype='application/json')
    except KeyError as argh:
        log.error("Key missing from data" + str(request))
        return Response('{"status": "failure", "reason": "Key missing in request."}',
                        status=400, mimetype='application/json')


def handle_finish(req: 'flask_request') -> None:
    """Extracts and handles data from a print success request."""
    data = extract_info(req)
    if data['topic'] == 'Print Done' and mail_sender is not None:
        mail_sender.send_finish_info(data['machine'], data['file'], data['time'])
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


@app.route("/jsonrpc", methods=['POST'])
@cross_origin()
def jsonrpc() -> str:
    return json_rpc_handler.process(request.json)


def make_filament_list(job: dict) -> list:
    result = []
    for key, value in job['filament'].items():
        tool = key
        length = value['length']
        volume = value['volume']
        result.append({'tool': tool, 'length': length, 'volume': volume})
    return result


def extract_info(req: 'flask_request') -> dict:
    data = {}
    extras = json.loads(req.form['extra'])
    job = json.loads(req.form['job'])
    data['file'] = extras['name']
    data['time'] = extras['time']
    data['topic'] = req.form['topic']
    data['machine'] = req.form['deviceIdentifier']
    data['tools'] = make_filament_list(job)
    log.info('New data: ' + str(data))
    return data


if __name__ == '__main__':
    app.run(host='0.0.0.0')
