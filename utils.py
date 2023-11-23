import logging

from twilio.rest import Client
from decouple import config
from sqlalchemy.exc import SQLAlchemyError

# internal imports
from models import Conversation


# set up twilio credentials
account_sid = config("TWILIO_ACCOUNT_SID")
auth_token = config("TWILIO_AUTH_TOKEN")
twilio_number = config("TWILIO_NUMBER")

client = Client(account_sid, auth_token)


# logging configuration
logging.basicConfig(filename='logs/bot.log', encoding='utf-8', format='%(asctime)s %(levelname)s: %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)


# Twilio Messaging API logic
def send_message(to_number, body_text):
    try:
        message = client.messages.create(
            from_ = f"whatsapp:{twilio_number}",
            body = body_text,
            to= f"whatsapp:{to_number}"
        )
        
        logger.info(f"Message sent to {to_number}: {message.body}\n")
        
    except Exception as e:
        logger.error(f"Error sending message to {to_number}: {e}")
        print("Messange not sent")
        
        
# store conversation in database
def store_conversation(db, whatsapp_number, body_text, response_text):
    try:
        conversation = Conversation(
            sender=whatsapp_number,
            message=body_text,
            response=response_text
        )
        
        db.add(conversation)
        db.commit()
        logger.info(f"Conversation #{conversation.id} stored in database")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error storing conversation in database: {e}")