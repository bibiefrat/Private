# content of conftest.py
import pytest
import smtplib

@pytest.fixture(scope="module")
def smtp_connection():
    return smtplib.SMTP_SSL_PORT("smtp.gmail.com", 587, timeout=5)