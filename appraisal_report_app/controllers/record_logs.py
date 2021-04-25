
import logging

logger = logging.getLogger(__name__)

def record_log(location, error_message):
    
    log_entry= f"error happened in {location}\n error was: {error_message}\n"
    logging.debug(log_entry)