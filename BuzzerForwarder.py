
import json
import os
import time
from datetime import date, datetime, timedelta
from functools import wraps

import boto3
from flask import Flask, abort, request
from flask.wrappers import Response
from twilio.twiml.messaging_response import Message, MessagingResponse
from twilio.twiml.voice_response import Dial, Number, VoiceResponse
from werkzeug.exceptions import BadRequestKeyError

from SecretManagerConrol import SecretManagerControl

app = Flask(__name__)



secret = SecretManagerControl(os.environ['secretARN'])

# FUNCTION: parse_NUMBERS(secret)
# PARAMS: secret
#   secret: secret object to parse the numbers from
# RETRUN: an array of the phone numbers
#
def parse_NUMBERS(secret):
	numString = secret["NUMBERS"]
	numArray = numString.split(',')

	return numArray


def validate_twilio_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if (request.values["AccountSid"] == secret["TWILIO_ACCOUNTSID"] and request.values["Caller"] == secret["BUZZERNUMBER"]):
                return f(*args, **kwargs)
            else:
                abort(403)
        except Exception:
            abort(403)

    return decorated_function

@app.route('/', methods = ['POST', 'GET'])
@validate_twilio_request #send to the validator
# FUNCTION: verifyCaller()
# PARAMS: none
# RETRUN: the voice response as a string, as per the twilio spec
#
def verifyCaller():

    resp = VoiceResponse()

    #error due to required items not in the header
    #secret cannot be called in authorizer. look into that
   
    call(resp)


    return str(resp)

# FUNCTION: call(resp)
# PARAMS: resp
#   resp: the voice response object to append the numbers
# RETRUN: none
#
def call(resp):
	
	dial = Dial()
	numbers = parse_NUMBERS(secret.values.NUMBERS)
	for number in numbers:
		dial.number(number)

	resp.append(dial)


	
@app.route('/mute', methods = ['POST', 'GET'])
@validate_twilio_request #send to the validator
def toggleMute():
    resp = MessagingResponse()

    try:
        messageBody = request.values["Body"]
        if messageBody.lower() == "unmute":
            resp.message("")
        elif parseTime(messageBody) != None:
            resp.message("you will not be desturbed until: [time]")
        else:
            resp.message("I didn't understand that message. [mute usage message]")

    except Exception:
        resp.message("something fucky happened serverside")

    return str(resp)

def parseTime(message):
    #this will be more robust later
    result = None
    try:
        #try and parse the time
        muteTime = time.strptime(message,"%I:%M %p")
        today = date.today()
        result = datetime.combine(muteTime, today)
        #if result is in the past apply the specified time to tommorrow
        if result < datetime.now() :
            result = datetime.combine(muteTime,today + timedelta(days= 1))
        #add more robust exception cases
    except Exception:
        try:
             result = datetime.strptime(message)
        except Exception:
            #failed either parser
            result = None
    return result

#Custom error page
#
@app.errorhandler(403)
def unauthorized(e):
    resp = VoiceResponse()
    resp.reject()
    return str(resp)
    #return "You are Unauthorized to visit this Website"


if __name__ == "__main__":
    app.run(debug=True)

	