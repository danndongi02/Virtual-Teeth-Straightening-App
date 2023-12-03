import os
import requests

from fastapi import FastAPI, Form, Depends, Request
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse

# Internal imports
from models import Conversation, SessionLocal
from utils import send_message, logger, store_conversation, detect_face, is_teeth_visible

# FastAPI setup
app = FastAPI()


# Values
company_name = config("COMPANY_NAME")
default_response = f"Hello. Thank you for contacting {company_name}. The bot is currently under development. Kindly bear with us"


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# root endpoint
'''
    method - "get"
    endpoint - "/"
    
    Return: {"msg": "Successfully running"}
'''
@app.get("/")
async def index():
    return {"msg": "Successfully running"}


# /message endpoint
'''
    method - "post"
    endpoint - "/message"
    
    request: Request object
    Body: Form data from incoming request
    db: Database session dependency
    
    return: "Success" after complete execution
'''
@app.post("/message")
async def reply(request: Request, Body = Form(), db: Session = Depends(get_db)):
    # Extract data from the incoming webhook request
    form_data = await request.form()
    
    profile_name = form_data['ProfileName'].split("whatsapp:")[-1]  # The sender's WhatsApp profile name
    whatsapp_number = form_data['From'].split("whatsapp:")[-1]      # The sender's WhatsApp number
    message = form_data['Body']                                     # The body of the incoming message
    num_media = int(form_data['NumMedia'])                          # The number of media items in the message
    
    
    # Response when image is received
    if num_media > 0:
        # Get media information from webhook information
        media_url = form_data['MediaUrl0']
        content_type = form_data['MediaContentType0']
        image = requests.get(media_url)
        print(f"Content type: {content_type}")
        
        # Check image type
        if content_type == "image/jpeg":
            filename = f"uploads\{message}.jpeg"
        elif content_type == "image/png":
            filename = f"uploads\{message}.png"
        elif content_type == "image/gif":
            filename = f"uploads\{message}.gif"
        else:
            filename = None
            
        # Save image locally
        if filename:
            if not os.path.exists(f'uploads\{profile_name}'):
                os.mkdir(f'uploads\{profile_name}')
            with open(filename, 'wb') as f:
                f.write(image.content)
                logger.info(f"Image saved successfully")
        
        
        # image path
        image_path = os.path.join(os.getcwd(), filename)
        logger.info(f"Image path: {image_path}")
        
        
        # check for faces
        logger.info("Checking for faces...")
        face_detected = detect_face(image_path)
        
        if face_detected:    
            logger.info("Checking for teeth visibility...")
            
            # detect teeth
            teeth_present = is_teeth_visible(image_path)
            
            if teeth_present:
                response = "Teeth detected"
                logger.info("Teeth detected")
            else:
                response = "No teeth detected"
                logger.info("No teeth detected")
            
        else:
            response = "No face detected. Please send an image with your face visible"
        
        
        # straighten_teeth(image_path)
        
    elif num_media == 0:
        response = default_response
    
    print(f"Response: {response}")    
    
    
    # Store the conversation in database
    store_conversation(db, whatsapp_number, Body, response)


    # send response
    logger.info(f"Sending response to {profile_name}: {whatsapp_number}")
    send_message(whatsapp_number, response)
    
    return "Success"