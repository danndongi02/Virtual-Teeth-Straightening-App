import logging

logging.basicConfig(filename='logs/logs2.log', encoding='utf-8', level=logging.INFO)
logging.info("This is a sample log message for info")
logging.error("This is a sample log message for error")