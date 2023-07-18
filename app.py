import os
from flask import Flask, request, abort
import requests
import json

app = Flask(__name__)

DEBUG = os.environ.get('DEBUG')
API_KEY = os.environ.get('API_KEY')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ALERT_CHAT_ID = os.environ.get('CHAT_ID')

@app.route('/send_message', methods=['POST'])
def send_message():
    # Check if the API key is valid
    api_key = request.headers.get('Authorization')
    if api_key != API_KEY:
        abort(401)

    # Get the message and chat_id from the POST request
    message = request.form['message']
    chat_id = request.form['chat_id']

    # Set the token for the Telegram bot
    bot_token = os.environ.get('BOT_TOKEN')

    # Set the URL for the Telegram Bot API
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    # Set the payload for the HTTP POST request
    payload = {
        'chat_id': chat_id,
        'text': message
    }

    # Send the HTTP POST request using the requests library
    response = requests.post(url, data=payload)

    # Check if the request was successful
    if response.status_code == 200:
        return 'Message sent successfully!'
    else:
        return 'Error sending message:', response.text

@app.route('/alertmanager', methods=['POST'])
def alertmanager():
    print("Something received:")
    # Check if the API key is valid
    api_key = request.headers.get('Authorization')[7:]
    print(f"Received API Key is: {api_key}")

    if api_key != API_KEY:
        abort(401)
    json_data = request.get_json()
    print(json.dumps(json_data, indent=2))
    data = {}
    data["receiver"] = json_data["receiver"] if "receiver" in json_data else "null"
    data["status"] = json_data["status"] if "status" in json_data else "null"
    data["alertname"] = json_data["alerts"][0]["labels"]["alertname"] if "alertname" in json_data["alerts"][0]["labels"] else "null"
    data["cluster"] = json_data["alerts"][0]["labels"]["cluster"] if "cluster" in json_data["alerts"][0]["labels"] else "null"
    data["exporter"] = json_data["alerts"][0]["labels"]["exporter"] if "exporter" in json_data["alerts"][0]["labels"] else "null"
    data["instance"] = json_data["alerts"][0]["labels"]["instance"] if "instance" in json_data["alerts"][0]["labels"] else "null"
    data["job"] = json_data["alerts"][0]["labels"]["job"] if "job" in json_data["alerts"][0]["labels"] else "null"
    data["severity"] = json_data["alerts"][0]["labels"]["severity"] if "severity" in json_data["alerts"][0]["labels"] else "null"
    data["startsAt"] = json_data["alerts"]["startsAt"] if "startsAt" in json_data["alerts"] else "null"
    data["endsAt"] = json_data["alerts"]["endsAt"] if "endsAt" in json_data["alerts"] else "null"
    if(data["status"] == "firing"): data["status"] = str("firing \U0001f525")
    elif (data["status"] == "resolved"): data["status"] = str("resolved \U00002705")
    # print(json.dumps(data, indent=2))

    message = "Alertmanager Alert Accurred!"+ "\n"+ \
    "Alert Receiver: "+ data["receiver"] + "\n"+ \
    "Alert Status: "+ data["status"] + "\n"+ \
    "Alert Name: "+ data["alertname"] + "\n"+ \
    "Cluster: "+ data["cluster"] + "\n"+ \
    "Exporter: "+ data["exporter"] + "\n"+ \
    "Instance: "+ data["instance"] + "\n"+ \
    "Job: "+ data["job"] + "\n"+ \
    "Severity: "+ data["severity"] + "\n"+ \
    "Starts At: "+ data["startsAt"] + "\n"+ \
    "Ends At: "+ data["endsAt"]

    bot_token = BOT_TOKEN
    # Set the URL for the Telegram Bot API
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    # Set the payload for the HTTP POST request
    payload = {
        'chat_id': ALERT_CHAT_ID,
        'text': message
    }

    # Send the HTTP POST request using the requests library
    response = requests.post(url, data=payload)

    # Check if the request was successful
    if response.status_code == 200:
        return 'Message sent successfully!'
    else:
        return 'Error sending message:', response.text

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=os.environ.get('DEBUG'))
