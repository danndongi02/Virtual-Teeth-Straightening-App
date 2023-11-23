import os
import requests

from fastapi import FastAPI, Form, Depends, Request
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse

# Internal imports
from models import Conversation, SessionLocal
from utils import send_message, logger, store_conversation

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
@app.get("/")
async def index():
    return {"msg": "Successfully running"}


# /message endpoint
@app.post("/message")
async def reply(request: Request, Body = Form(), db: Session = Depends(get_db)):
    # Extract data from the incoming webhook request
    form_data = await request.form()
    
    profile_name = form_data['ProfileName'].split("whatsapp:")[-1]  # The sender's WhatsApp profile name
    whatsapp_number = form_data['From'].split("whatsapp:")[-1]      # The sender's WhatsApp number
    message = form_data['Body']                                     # The body of the incoming message
    num_media = int(form_data['NumMedia'])                          # The number of media items in the message
    
    logger.info(f"Sending response to {profile_name}: {whatsapp_number}")
    
    
    # Response when image is received
    # Image logic after it has been received
    if num_media > 0:
        media_url = form_data['MediaUrl0']
        content_type = form_data['MediaContentType0']
        r = requests.get(media_url)
        print(content_type)
        
        if content_type == "image/jpeg":
            filename = f"uploads/{profile_name}/{message}.jpg"
        elif content_type == "image/png":
            filename = f"uploads/{profile_name}/{message}.png"
        elif content_type == "image/gif":
            filename = f"uploads/{profile_name}/{message}.gif"
        else:
            filename = None
            
        if filename:
            if not os.path.exists(f'uploads/{profile_name}'):
                os.mkdir(f'uploads/{profile_name}')
            with open(filename, 'wb') as f:
                f.write(r.content)
        
        
        response = f"Thank you {profile_name}! Your image has been received"
        logger.info(f"Image received from {profile_name}: {whatsapp_number}")
        
    elif num_media == 0:
        response = default_response
    
    print(response)    
    
    
    # Store the conversation in database
    store_conversation(db, whatsapp_number, response, Body)


    # send response
    send_message(whatsapp_number, response)
    
    return "Success"