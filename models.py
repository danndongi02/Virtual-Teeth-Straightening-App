from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker
from decouple import config


# create the URL object used as the argument for the create_engine function
url = URL.create(
    drivername="postgresql",
    username=config("DB_USER"),
    password=config("DB_PASSWORD"),
    host=config("DB_HOST"),
    port=config("DB_PORT"),
    database=config("DB_NAME"),
)


# create an engine object that manages connections to the database using a URL that contains the connection information
engine = create_engine(url)


# create session objects used to interact with the database
SessionLocal = sessionmaker(bind=engine)


# create a base class to be used to define mapped classes for the ORM
Base = declarative_base()



class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String)
    message = Column(String)
    response = Column(String)
    
Base.metadata.create_all(engine)
