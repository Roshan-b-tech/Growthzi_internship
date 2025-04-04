from flask import current_app
from flask_mail import Message
import logging

def send_email(subject, recipients, body, html=None):
    """
    Send an email using Flask-Mail.
    
    Args:
        subject (str): Email subject
        recipients (list): List of recipient email addresses
        body (str): Plain text email body
        html (str, optional): HTML email body
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=body,
            html=html
        )
        current_app.mail.send(msg)
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        return False 