import logging

from twilio.rest import Client
from decouple import config


# set up twilio credentials
account_sid = config("TWILIO_ACCOUNT_SID")
auth_token = config("TWILIO_AUTH_TOKEN")
twilio_number = config("TWILIO_NUMBER")

client = Client(account_sid, auth_token)


# logging configuration
logging.basicConfig(filename='sample.log', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)


# Twilio Messaging API logic
def send_message(to_number, body_text):
    try:
        message = client.messages.create(
            from_ = f"whatsapp: {twilio_number}",
            body = body_text,
            to= f"whatsapp: {to_number}"
        )
        
        logger.info(f"Message sent to {to_number}: {message.body}")
        
    except Exception as e:
        logger.error(f"Error sending message to {to_number}: {e}")