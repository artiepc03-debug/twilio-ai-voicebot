from twilio.rest import Client
import smtplib, os

def send_summary(text):
    client = Client(os.getenv("TWILIO_ACCOUNT_SID"),
                    os.getenv("TWILIO_AUTH_TOKEN"))

    client.messages.create(
        to=os.getenv("ALERT_PHONE"),
        from_=os.getenv("TWILIO_NUMBER"),
        body=text
    )
