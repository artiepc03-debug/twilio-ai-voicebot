import os
from twilio.rest import Client

client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

def sms_you(summary):
    client.messages.create(
        to=os.getenv("ALERT_PHONE"),
        from_=os.getenv("TWILIO_NUMBER"),
        body=summary
    )

def sms_caller(number, message):
    client.messages.create(
        to=number,
        from_=os.getenv("TWILIO_NUMBER"),
        body=message
    )
