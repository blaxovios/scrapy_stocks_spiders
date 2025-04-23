import unittest
from scrapy.http import Response
from stocks_spider.utils import generate_uuid
import hashlib
from uuid import uuid5, NAMESPACE_DNS
from urllib.parse import urlsplit, urlunsplit
import logging
import io
from unittest.mock import patch
from stocks_spider.utils import setup_logging

class TestGenerateUUID(unittest.TestCase):

    def test_valid_response(self):
        response = Response(url='https://example.com', body=b'test content')
        uuid = generate_uuid(response)
        self.assertIsInstance(uuid, str)

    def test_non_bytes_like_body(self):
        response = Response(url='[https://example.com](https://example.com)', body=b'test content')
        uuid = generate_uuid(response)
        self.assertIsInstance(uuid, str)

    def test_invalid_url(self):
        response = Response(url='invalid_url', body=b'test content')
        uuid = generate_uuid(response)
        self.assertIsInstance(uuid, str)

    def test_none_body(self):
        response = Response(url='https://example.com', body=None)
        uuid = generate_uuid(response)
        self.assertIsInstance(uuid, str)

    def test_none_url(self):
        response = Response(url='', body=b'test content')
        uuid = generate_uuid(response)
        self.assertIsInstance(uuid, str)

    def test_uuid_generation(self):
        response = Response(url='https://example.com', body=b'test content')
        uuid = generate_uuid(response)
        # Verify that the UUID is generated correctly
        parsed_url = urlsplit(response.url)
        normalized_url = urlunsplit((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', ''))
        content_hash = hashlib.sha256(response.body).hexdigest()
        expected_uuid = str(uuid5(NAMESPACE_DNS, f"{normalized_url}:{content_hash}"))
        self.assertEqual(uuid, expected_uuid)


class TestSetupLogging(unittest.TestCase):
    @patch('logging.root.handlers')
    @patch('logging.Formatter')
    @patch('logging.StreamHandler', side_effect=io.UnsupportedOperation('not readable'))
    @patch('logging.handlers.RotatingFileHandler')
    def test_default_logging_setup(self, mock_rotating_file_handler, mock_stream_handler, mock_formatter, mock_handlers):
        with self.assertRaises(io.UnsupportedOperation):
            setup_logging()

    @patch('logging.root.handlers')
    @patch('logging.Formatter')
    @patch('logging.StreamHandler', side_effect=io.UnsupportedOperation('not readable'))
    @patch('logging.handlers.RotatingFileHandler')
    def test_logging_setup_with_debug_level(self, mock_rotating_file_handler, mock_stream_handler, mock_formatter, mock_handlers):
        with self.assertRaises(io.UnsupportedOperation):
            setup_logging(console_level=logging.DEBUG)

    @patch('logging.root.handlers')
    @patch('logging.Formatter')
    @patch('logging.StreamHandler', side_effect=io.UnsupportedOperation('not readable'))
    @patch('logging.handlers.RotatingFileHandler')
    def test_logging_setup_with_custom_debug_filename(self, mock_rotating_file_handler, mock_stream_handler, mock_formatter, mock_handlers):
        with self.assertRaises(io.UnsupportedOperation):
            setup_logging(debug_filename='custom_debug')

    @patch('logging.root.handlers')
    @patch('logging.Formatter')
    @patch('logging.StreamHandler', side_effect=io.UnsupportedOperation('not readable'))
    @patch('logging.handlers.RotatingFileHandler')
    def test_logging_setup_with_existing_handlers(self, mock_rotating_file_handler, mock_stream_handler, mock_formatter, mock_handlers):
        with self.assertRaises(io.UnsupportedOperation):
            setup_logging()

    @patch('logging.root.handlers')
    @patch('logging.Formatter')
    @patch('logging.StreamHandler')
    @patch('logging.handlers.RotatingFileHandler')
    def test_logging_setup_with_invalid_console_level(self, mock_rotating_file_handler, mock_stream_handler, mock_formatter, mock_handlers):
        with self.assertRaises(ValueError):
            setup_logging(console_level='invalid_level')
