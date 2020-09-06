from flask import Flask, request
import json
from mysql_connection import Connector
from datetime import datetime

app = Flask(__name__)
fp = open('config.json', 'r')
config = json.load(fp)

connector = Connector(config['dbconfig'])


@app.route("/webhook", methods=['POST'])
def webhook() -> str:
    """This method is the webhook endpoint"""
    identifier = request.form['deviceIdentifier']
    extras = json.loads(request.form['extra'])
    topic = request.form['topic']
    if topic == 'Print Done' or topic == 'Print Failed':
        handle_finish(request)
    return "success"


def handle_finish(req: 'flask_request') -> None:
    """Extracts and handles data from a print success request."""
    data = extract_info(req)
    connector.save(**data)


@app.route("/data", methods=['GET'])
def get_data() -> str:
    data = connector.load_data()
    print(data)
    for line in data:
        line['DATE'] = datetime.timestamp(line['DATE'])
    return json.dumps(data)


def extract_info(req: 'flask_request') -> dict:
    data = {}
    extras = json.loads(request.form['extra'])
    data['file'] = extras['name']
    data['time'] = extras['time']
    data['topic'] = req.form['topic']
    data['machine'] = req.form['deviceIdentifier']
    return data


def log(line: str) -> None:
    """Logs a line to the chosen log system."""
    with open("log", "a+") as file:
        file.write(str(datetime.now()) + '\t' + line + '\n')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
