import logging
import cv2

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
logging.basicConfig(filename='logs/detect_teeth.log', encoding='utf-8', format='%(asctime)s %(levelname)s: %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
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
        print("Message not sent")
        
        
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
        

# identify teeth
def detect_teeth(image_path):
    # read image
    try:
        image = cv2.imread(fr"{image_path}")
        logger.info(f"Image read successfully")
    except Exception as e:
        print(f"Error reading image: {e}")
        logger.info(f"Error reading image: {e}")
        response = "Couldn't read image!"
        # return response
    
    # convert to grayscale
    try:
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        logger.info(f"Image converted to grayscale")
    except Exception as e:
        print(f"Error converting image to grayscale: {e}")
        logger.info(f"Error converting image to grayscale: {e}")
        response = "Couldn't convert image to grayscale!"
        # return response
    
    # apply face detection using Haar Cascade classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray_image, 1.1, 4)
    
    # if no faces detected
    if len(faces) == 0:
        print("No faces detected")
        response = "No teeth detected"
        return response
    
    
    # for each detected face, identify teeth using smile detection
    for (x, y, w, h) in faces:
        face_region = gray_image[y:y+h, x:x+w]
        
        # apply smile detection using Haar Cascade classifier
        smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        smiles = smile_cascade.detectMultiScale(face_region, 1.1, 4)
        
        # if smile detected
        if len(smiles) > 0:
            print("Smile detected")
            response = "Teeth detected"
            return response
        
    response = "No teeth detected"
    return response