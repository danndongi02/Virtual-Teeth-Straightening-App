from fastapi import FastAPI, Form, Depends, Request
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse

# Internal imports
from models import Conversation, SessionLocal
from utils import send_message, logger

# FastAPI setup
app = FastAPI()


# Variables
company_name = config("COMPANY_NAME")

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
async def reply(request: Request, Body: str = Form(), db: Session = Depends(get_db)):
    # Extract phone number from the incoming webhook request
    form_data = await request.form()
    profile_name = form_data['ProfileName'].split("whatsapp:")[-1]
    whatsapp_number = form_data['From'].split("whatsapp:")[-1]
    # print(f"Whatsapp number: {whatsapp_number}")
    print(f"Sending response to {profile_name}: {whatsapp_number}")
    
    
    # sample response
    response = f"Hello. Thank you for contacting {company_name}. The bot is currently under development. Kindly bear with us"
    print(response)
    
    
    # Store the conversation in database
    try:
        conversation = Conversation(
            sender=whatsapp_number,
            message=Body,
            response=response
        )
        
        db.add(conversation)
        db.commit()
        logger.info(f"Conversation #{conversation.id} stored in database")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error storing conversation in database: {e}")
        
    send_message(whatsapp_number, response)
    
    return "Success"