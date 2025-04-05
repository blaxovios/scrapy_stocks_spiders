import hashlib
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid5, NAMESPACE_DNS
from scrapy import http


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