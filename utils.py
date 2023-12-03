import logging
import cv2
import numpy as np
import dlib
import face_recognition

from PIL import Image, ImageDraw
from scipy.datasets import face
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


'''
    send_message - Send message through Twilio API
    
    to_number: recipient's WhatsApp number
    body_text: response to message received
'''
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
        
        
'''
    store_conversation - Store conversation in database
    
    db: database session
    whatsapp_number: sender's WhatsApp number
    body_text: body of the message
    response_text: response to the message
    
'''
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
        

'''
    preprocess_image - Preprocess the image to be analyzed
    
    image_path: path to image being processed
    
    Return: faces - list of faces detected in the image
            gray_image - grayscale image
'''
def preprocess_image(image_path):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # read image
    try:
        image = cv2.imread(fr"{image_path}")
        logger.info(f"Image read successfully")
    except Exception as e:
        # print(f"Error reading image: {e}")
        logger.info(f"Error reading image: {e}")
    
    # convert to grayscale
    try:
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        logger.info(f"Image converted to grayscale")
    except Exception as e:
        # print(f"Error converting image to grayscale: {e}")
        logger.info(f"Error converting image to grayscale: {e}")
    
    # apply face detection using Haar Cascade classifier
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
    
    return faces, gray_image
    

'''
    detect_face - Check for faces in the image provided
    
    image_path: image to be analyzed
    
    Return: False - no faces found
            True - face(s) found
'''
def detect_face(image_path):
    face_present = False
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    
    logger.info(f"{len(face_locations)} faces(s) found")

    # If faces found
    if len(face_locations) > 0:
        face_present = True    
        
    return face_present


'''
    is_teeth_visible - Check the visibility of teeth in the image provided.
    
    @image_path: path to image being processed.
    
    Return: False - Teeth not visible
            True - Teeth visible
'''
def is_teeth_visible(image_path):
    # Load the image
    image = cv2.imread(image_path)
    
    # Load the Haar Cascade classifier for teeth
    teeth_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
    
    faces, gray = preprocess_image(image_path)
    
    
    # Assume that the teeth are not visible initially
    teeth_visible = False
    
    # For each face detected
    for (x, y, w, h) in faces:
        # Get the region of interest for the face
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = image[y:y+h, x:x+w]
        
        # Detect teeth in the face
        teeth = teeth_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
        
        # If any teeth are detected
        if len(teeth) > 0:
            # The teeth are visible
            teeth_visible = True
            break
    
    # Return whether the teeth are visible or not
    return teeth_visible
    


'''
    straighten_teeth - Straighten teeth in the image provided.
    
    image_path: path to image being processed.
'''
def straighten_teeth(image_path):
    def transform_coordinates(x, y):
        # Define your transformation logic here
        new_x = x
        new_y = y
        return new_x, new_y

    # preprocess image
    faces, gray_image = preprocess_image(image_path)

    # apply Canny edge detection
    edges = cv2.Canny(gray_image, 50, 150)

    # find circles in the image
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, 20, minRadius=40, maxRadius=100)
    circles = np.uint16(np.around(circles))

    # straighten_teeth
    for circle in circles[0]:
        x, y, r = circle

        # apply some transformation to straighten teeth
        new_x, new_y = transform_coordinates(x, y)
        new_image = cv2.circle(image_path, (int(new_x), int(new_y)), int(r), (0, 255, 0), 2)
        
    cv2.imwrite('uploads\processed', new_image)
    
    logger.info(f"Image straightened successfully")
