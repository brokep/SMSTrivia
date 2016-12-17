#!/usr/bin/env python
from twilio.rest import TwilioRestClient
from flask import Flask, request, redirect, session
import twilio.twiml
import os
import threading
from TriviaWindow import TriviaWindow
from PySide.QtGui import QApplication, QIcon
import sys
import requests

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = os.urandom(24)


def runFlask():
    app.run(debug=True, use_reloader=False)

@app.route("/", methods=['GET', 'POST'])
def respond():
    resp = twilio.twiml.Response()
    state = int(session.get('state',0))
    rx = request.values.get('Body')
    sender = request.values.get('From')

    if(window.centralWidget().registrationActive):
        if(state == 0):
            if(rx.lower().strip() == 'join'):
                tx = "You have now joined Lake Orion Swim and Dive Trivia!\nGood luck!"
                state = 1
                window.centralWidget().registerUser(sender)
            else:
                tx = "Welcome to Lake Orion Swim and Dive Trivia!\nReply JOIN to join today's trivia challenge."

        elif(state == 1):
            tx = "You have already joined Lake Orion Swim and Dive Trivia!\nPlease wait for the registration period to finish."

        session['state'] = state

    elif(window.centralWidget().questionActive):
        if(state == 0):
            tx = "Welcome to Lake Orion Swim and Dive Trivia!\nRegistration is currently closed, please try again next time."
        elif(state == 1):
            answer = rx
            window.centralWidget().putAnswer(sender, answer)
            tx = "You selected answer: " + answer + ".\nPlease check that this is your desired answer. Feel free to change your answer before time runs out."
    else:
        tx = "Sorry, there is no current active session"
    resp.sms(tx)
    return str(resp)

@app.route('/exit', methods=['POST'])
def exit():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "Shutting down..."

flaskThread = threading.Thread(target=runFlask)
flaskThread.start()
qapp = QApplication(sys.argv)
qapp.setWindowIcon(QIcon("./icon.png"))
window = TriviaWindow()

qapp.exec_()

requests.post('http://localhost:5000/exit')
flaskThread.join()
sys.exit()
