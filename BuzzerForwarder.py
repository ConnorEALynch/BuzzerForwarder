
import os
from enum import Enum
from functools import wraps

from flask import Flask, abort, redirect, request
from twilio.twiml.messaging_response import Message, MessagingResponse
from twilio.twiml.voice_response import Dial, Number, VoiceResponse
from werkzeug.exceptions import HTTPException

from MuteManager import MuteManger
from SecretManagerConrol import SecretManagerControl

app = Flask(__name__)

##Globals

#casues crashes if configured improperly. research solutions
secret = SecretManagerControl(os.environ["secretARN"])
muter = MuteManger(secret)



## Validators and Authorizors

# 	def authorize_account()
#   PARAMS: None
#	RETRUN: true or false depending on if the accoundSID exists and matches the expected
#	
def authorize_account():
    result = False
    if "AccountSid" in request.values and request.values["AccountSid"] == secret.values["TWILIO_ACCOUNTSID"]:
        result = True
    return result

# 	def validate_initial_request(f) @wraps decorated_function(*args, **kwargs)
#	RETRUN: true or false depending on if the accoundSID exists and matches the expected
#	
def validate_initial_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            #if authorized redirect the request to the specified route if it contains the appropriate request values
            if authorize_account():
                if "CallSid" in request.values:
                    return redirect('/call')
                elif "MessageSid" in request.values:
                    return redirect('/mute')
                else:
                    return f(*args, **kwargs)     
            else:
                raise HTTPException
        except HTTPException:
            print(HTTPException)
            abort(403)
        except Exception as e:
            print(e)
            abort(500)

    return decorated_function



#  def handle_error(erno, invoke=None)
# 	PARAMS: erno, invoke=None
#   	erno: the http status code that should be invoked
# 		request: the request object will look for the related ID to the call or message and determine the proper response
#	RETRUN: a string to gracefull terminate a call/text with relivent information or display error page for web invoke
#
def handle_error(erno, request):
    errorMessage = "Internal Server Error"
    #if its a call reject it, if internal error say error and reject
    if "CallSid" in request.values:
        resp = VoiceResponse()
        if(erno == 500):
            resp.say(errorMessage)
            resp.hangup()
        else:
            resp.reject()
        return str(resp)
    #if its a text and an internal error send a reponse
    if "MessageSid" in request.values and erno == 500:
        resp = MessagingResponse()
        resp.message(errorMessage)
        return str(resp)
    #otherwise display error page
    abort(erno)

# 	def validate_message_request(f) @wraps decorated_function(*args, **kwargs)
#	RETRUN: true or false depending on if the accoundSID exists and matches the expected
#
def validate_message_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if authorize_account() and request.values["From"] in secret.values["NUMBERS"]:
                    return f(*args, **kwargs)
            else:
                raise HTTPException
        except HTTPException:
            return handle_error(403, request)
        except Exception as e:
            print(e)
            return handle_error(500, request)

    return decorated_function

# 	def validate_call_request(f) @wraps decorated_function(*args, **kwargs)
#	RETRUN: true or false depending on if the accoundSID exists and matches the expected
#
def validate_call_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if (authorize_account() and request.values["From"] == secret.values["BUZZERNUMBER"]):
                return f(*args, **kwargs)

            else:
                raise HTTPException
        except HTTPException:
            print(HTTPException)
            return handle_error(403, request)
        except Exception as e:
            print(e)
            return handle_error(500, request)

    return decorated_function
    



    
##REST endpoints
@app.route('/', methods = ['POST', 'GET'])
@validate_initial_request
def index():
    #I may make this a summary or statistic page in the future. for now it does not exist
    abort(404)


@app.route('/call', methods = ['POST', 'GET'])
@validate_call_request #send to the validator
# FUNCTION: callTenants()
# PARAMS: none
# RETRUN: the voice response as a string, as per the twilio spec
#
def call_tenants():
    
    resp = VoiceResponse()
    dial = Dial()
    try:
    #append all numbers that the mutemanager has determined are active
        if not muter.bothMute:
            for num in muter.callList:
                dial.number(num)

            resp.append(dial)
        else:
            resp.reject()
        return str(resp)
    except Exception as e:
        print(e)
        return handle_error(500, request)




@app.route('/mute', methods = ['POST', 'GET'])
@validate_message_request #send to the validator
# FUNCTION: toggle_mute()
# PARAMS: none
# RETRUN: the voice response as a string, as per the twilio spec
#
def toggle_mute():
    resp = MessagingResponse()
    message = Message()
    try:
        message.body(muter.manage_request(request))
        secret.update_mute(muter)
        resp.append(message)
        #check if both are muted
        if muter.bothMute:
            resp.message("WARNING: Both Tenants Muted")
        return str(resp)
    except Exception as e:
        print(e)
        return handle_error(500, request)
    

if __name__ == "__main__":
    app.run(debug=False)

	