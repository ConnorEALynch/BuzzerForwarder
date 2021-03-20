
import json
import os
from functools import wraps

import boto3
from flask import Flask, abort, request
from twilio.twiml.voice_response import Dial, Number, VoiceResponse
from werkzeug.exceptions import BadRequestKeyError

app = Flask(__name__)


# FUNCTION: def get_secret_value(name, version=None)
# PARAMS:
#   name: the ARN of the secret manager
#   version=None: secret version default is none
# RETRUN: an object with 
#
def get_secret_value(name, version=None):
    secrets_client = boto3.client("secretsmanager", region_name='us-east-1')
    kwargs = {'SecretId': name}
    if version is not None:
        kwargs['VersionStage'] = version
    response = secrets_client.get_secret_value(**kwargs)
    return json.loads(response["SecretString"])

secret = get_secret_value(os.environ['secretARN'])

# FUNCTION: parse_NUMBERS(secret)
# PARAMS: secret
#   secret: secret object to parse the numbers from
# RETRUN: an array of the phone numbers
#
def parse_NUMBERS(secret):
	numString = secret["NUMBERS"]
	numArray = numString.split(',')

	return numArray


# FUNCTION: validate_twilio_request()
# PARAMS: none
# RETRUN: true or flase based on if the medium strength auth
#
def validate_twilio_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if (request.values["AccountSid"] == secret["TWILIO_ACCOUNTSID"] and request.values["Caller"] == secret["BUZZERNUMBER"]):
                return f(*args, **kwargs)
            else:
                abort(403)
        except BadRequestKeyError:
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
	numbers = parse_NUMBERS(secret)
	for number in numbers:
		dial.number(
			number
		)
	resp.append(dial)
	
#Custom error page
#
@app.errorhandler(403)
def unauthorized(e):
    return "You are Unauthorized to visit this Website"


if __name__ == "__main__":
    app.run(debug=True)

	