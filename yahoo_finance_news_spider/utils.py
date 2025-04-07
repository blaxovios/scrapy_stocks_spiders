import hashlib
from urllib.parse import urlsplit, urlunsplit, urlparse, urlunparse
from uuid import uuid5, NAMESPACE_DNS
from scrapy import http
import logging
from logging.handlers import RotatingFileHandler
import datetime


def setup_logging(debug_filename: str = 'debug', console_level: int = logging.INFO) -> None:
    """Attach default Cloud Logging handler to the root logger."""
    logging.root.setLevel(console_level)
    
    # Clear existing handlers
    if logging.root.hasHandlers():
        logging.root.handlers.clear()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Get current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Add rotating file handler to log to a file
    file_handler = RotatingFileHandler(f'logs/{debug_filename}_{timestamp}.log', maxBytes=50*1024*1024, backupCount=5)
    file_handler.setLevel(console_level)
    file_handler.setFormatter(formatter)
    logging.root.addHandler(file_handler)

    # Only add console handler if console_level is not DEBUG
    if console_level != logging.DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        logging.root.addHandler(console_handler)

    logging.info("Local logging setup complete")
    
    # Print current handlers after setup
    print("Handlers after setup:", logging.root.handlers)

def generate_uuid(response: http.Response) -> str:
    """
    Generate a UUID for a Scrapy response.

    The UUID is based on the normalized URL and the content hash of the response body.
    This ensures that the same URL with the same content will always produce the same UUID.

    Parameters:
    - response (scrapy.http.Response): The response to generate a UUID for.

    Returns:
    - str: The generated UUID.
    """
    
    try:
        content_hash = hashlib.sha256(response.body).hexdigest()
    except (TypeError, AttributeError):
        return str(uuid5(NAMESPACE_DNS, response.url))

    try:
        parsed_url = urlsplit(response.url)
        # Normalize the URL
        normalized_url = urlunsplit((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', ''))
    except (TypeError, ValueError, AttributeError):
        return str(uuid5(NAMESPACE_DNS, response.url))

    uuid_str = f"{normalized_url}:{content_hash}"
    return str(uuid5(NAMESPACE_DNS, uuid_str))       
 
def normalize_url(url):
    """
    Normalize the URL by removing trailing slashes from the path.
    You can extend this function for further normalization.
    """
    parts = urlparse(url)
    normalized_path = parts.path.rstrip('/')
    return urlunparse((parts.scheme, parts.netloc, normalized_path, parts.params, parts.query, parts.fragment))