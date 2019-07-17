import json
import os

from urllib.request import urlopen, Request

def sendToPushover(msg):
     appToken = os.environ.get('PushoverAppToken')
     userKey = os.environ.get('PushoverUserToken')
     data = {"token": appToken, "user": userKey, "message": msg}
     rq = Request("https://api.pushover.net/1/messages.json",
                  data=json.dumps(data).encode("utf8"),
                  headers={'content-type': 'application/json'})
     return urlopen(rq)
     
     

def lambda_handler(event, context):
    print(event)
    resp = ''
    if 'queryStringParameters' in event:
        qsp = event['queryStringParameters']    
        if 'SmsSid' in qsp:
            b = qsp["Body"]
            f = qsp["From"]
            msg = f"{f} says: '{b}'"
            print(msg)
            sendToPushover(msg)
            forward = os.environ.get('ForwardTo')
            if f == forward:
                (r,v) = b.split(': ')
                resp = f'<Message to="{r}">{v}</Message>'
            else:
                resp = f'<Message to="{forward}">{f}: {b}</Message>'
            
        if 'CallSid' in qsp:
            dir = qsp['Direction']
            caller = qsp['Caller']
            called = qsp['Called']
            fr = qsp['From']
            to = qsp['To']
            twilioNumber = os.environ.get('TwilioNumber')
            if 'SipCallId' in qsp:
                callerId = twilioNumber
                forward = to.strip('sip:').split('@')[0]
                user = fr.strip('sip:').split('@')[0]
                sendToPushover(f'Internal call from {user} to {forward}')
            else:
                callerId = fr
                forward = os.environ.get('ForwardTo')
                sendToPushover(f'Call from {fr} to {to}')
            resp = f'<Dial callerId="{callerId}">{forward}</Dial>'
    print(resp)
    return { 'statusCode': 200
           , 'body': f'<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response>{resp}</Response>'
           , 'headers': {"content-type": "text/xml"}
    }
