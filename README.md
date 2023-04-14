This is a webhook endpoint for the excellent OctoPrint-Webhooks plugin by Blane Townsend. It can be found here:
https://plugins.octoprint.org/plugins/webhooks/

## 1 Setup
Just put the files somewhere and run them with a Python WSGI. Personally, I use Gunicorn and start the app with "gunicorn -b 0.0.0.0 webapp:app --daemon". 
This is a Flask application, so you will need Flask to run this.
You will need a database for this to function. Currently, the application only supports MySQL or MariaDB.
The application will run on port 5000 by default.

### 1.1 Requirements
- Python 3.7 or higher
- A Python WSGI
- A MySQL or MariaDB database
- Flask (https://flask.palletsprojects.com/en/2.2.x/). You can install this by running 'pip install Flask'. Consider setting up a venv for this.

## 2 Configuration
There are several configuration option. First, rename the config.json.example to config.json. Afterwards, you have the following options:

- dbtype: Leave that as is, or remove it. It doesn't do anything for now.
- dbconfig: Where to find your db and with which user. The database / schema and the user must exist, the tables will be added by the app if they are missing.
- webhook_key: This is optional. The webhook can send a key for authentication with your app. If you leave this blank or remove it altogether, the application will not check it. Otherwise, it must match.
- mailconfig: This is optional. Data about your mail server, so the application can send you mails once a print finishes. Should work with most servers.

## 3 JSON-RPC
The app provides a JSON-RPC 2.0 (https://www.jsonrpc.org/specification) implementation. It can be found under /jsonrpc.

These methods are available to call:
- CALCULATOR.PRINT_TIME
- CALCULATOR.NUMBERS_BY_PRINTERS
- CALCULATOR.NUMBERS_BY_PRINTERS_CLEANED
- CALCULATOR.MEAN_PRINT_LENGTH
- CALCULATOR.PRINTS_BY_MONTH_AND_PRINTER
- CALCULATOR.FAIL_RATE_BY_PRINTERS
- CALCULATOR.CUMULATIVE_PRINTS
- CALCULATOR.ALL_DATA

None of these methods require any parameters, and they are read-only. For reference what they do, please consult the docstrings in the statistics_calculator.py file. Return values are converted into valid JSON.