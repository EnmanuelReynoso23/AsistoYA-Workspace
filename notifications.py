import requests
import json
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import base64
import hashlib

class NotificationManager:
    def __init__(self, api_url=None, api_key=None, twilio_sid=None, twilio_token=None, twilio_phone=None,
                 email_user=None, email_password=None, email_smtp=None, email_port=587):
        """
        Initialize notification manager with optional WhatsApp API, Twilio, and email credentials
        """
        self.api_url = api_url
        self.api_key = api_key
        self.history = []
        self.load_history()
        
        # Twilio configuration
        self.twilio_client = None
        self.twilio_phone = twilio_phone
        if twilio_sid and twilio_token and twilio_phone:
            try:
                from twilio.rest import Client
                self.twilio_client = Client(twilio_sid, twilio_token)
                print("Twilio SMS client configured successfully")
            except ImportError:
                print("Twilio package not installed. SMS notifications will be unavailable.")
            except Exception as e:
                print(f"Error configuring Twilio client: {e}")
        
        # Email configuration
        self.email_configured = False
        self.email_user = email_user
        self.email_password = email_password
        self.email_smtp = email_smtp
        self.email_port = email_port
        
        if email_user and email_password and email_smtp:
            self.email_configured = True
            print("Email notification system configured successfully")
    
    def send_whatsapp(self, phone_number, message):
        """
        Send a message via WhatsApp API
        """
        if not self.api_url or not self.api_key:
            print("WhatsApp API not configured")
            return False
            
        try:
            # Format phone number for WhatsApp API
            formatted_phone = phone_number.replace('+', '').replace(' ', '')
            
            # Create WhatsApp URL with phone and message
            whatsapp_url = f"{self.api_url}?phone={formatted_phone}&text={requests.utils.quote(message)}"
            
            payload = {"url": whatsapp_url}
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.api_url, data=json.dumps(payload), headers=headers)
            
            if response.status_code == 200:
                print(f"WhatsApp message sent successfully to {phone_number}")
                self.log_notification(phone_number, message, "whatsapp")
                return True
            else:
                print(f"Failed to send WhatsApp message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return False

    def send_sms(self, phone_number, message):
        """
        Send an SMS message via Twilio
        """
        if not self.twilio_client:
            print("Twilio client not configured")
            return False
            
        try:
            # Format phone number for Twilio
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number
                
            twilio_message = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=phone_number
            )
            
            print(f"SMS sent successfully to {phone_number} with SID: {twilio_message.sid}")
            self.log_notification(phone_number, message, "sms")
            return True
            
        except Exception as e:
            print(f"Failed to send SMS: {e}")
            return False

    def send_email(self, recipient_email, subject, message, attachments=None):
        """
        Send an email notification with optional attachments
        """
        if not self.email_configured:
            print("Email not configured")
            return False
            
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add text part
            msg.attach(MIMEText(message, 'html'))
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as file:
                            attachment = MIMEApplication(file.read())
                            attachment.add_header('Content-Disposition', 'attachment', 
                                                 filename=os.path.basename(file_path))
                            msg.attach(attachment)
            
            # Create secure connection and send
            context = ssl.create_default_context()
            with smtplib.SMTP(self.email_smtp, self.email_port) as server:
                server.starttls(context=context)
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            print(f"Email sent successfully to {recipient_email}")
            self.log_notification(recipient_email, subject, "email")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def send_tutor_notification(self, tutor_contact, student_name, status, course_name=None, template=None):
        """
        Send notification to tutor about student attendance
        """
        # Default templates
        templates = {
            "present": f"📚 {student_name} ha sido registrado como presente en la clase de {course_name or 'hoy'}.",
            "absent": f"⚠️ {student_name} no ha asistido a la clase de {course_name or 'hoy'}.",
            "late": f"🕒 {student_name} llegó tarde a la clase de {course_name or 'hoy'}."
        }
        
        # Use provided template or default one
        message = template or templates.get(status.lower(), templates["present"])
        
        # Replace placeholders
        message = message.replace("{{Nombre}}", student_name)
        message = message.replace("{{Curso}}", course_name or "")
        message = message.replace("{{Estado}}", status)
        
        # Check if we have email or phone
        if "email" in tutor_contact and tutor_contact["email"]:
            subject = f"Notificación de asistencia - {student_name}"
            return self.send_email(tutor_contact["email"], subject, message)
        elif "phone" in tutor_contact and tutor_contact["phone"]:
            # Try SMS first, then WhatsApp as fallback
            if self.twilio_client:
                return self.send_sms(tutor_contact["phone"], message)
            elif self.api_url:
                return self.send_whatsapp(tutor_contact["phone"], message)
        
        print(f"No valid contact method for tutor of {student_name}")
        return False

    def log_notification(self, recipient, message, method="unknown"):
        """
        Log a notification in the history
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({
            "recipient": recipient,
            "message": message,
            "method": method,
            "timestamp": timestamp
        })
        self.save_history()

    def get_notification_history(self, limit=None, method=None):
        """
        Get notification history with optional filtering
        """
        filtered = self.history
        
        if method:
            filtered = [n for n in filtered if n.get("method") == method]
            
        if limit and limit > 0:
            filtered = filtered[-limit:]
            
        return filtered
        
    def save_history(self):
        """
        Save notification history to file
        """
        try:
            # Create data directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            
            with open("data/notification_history.json", "w") as f:
                json.dump(self.history, f)
        except Exception as e:
            print(f"Error saving notification history: {e}")
            
    def load_history(self):
        """
        Load notification history from file
        """
        try:
            if os.path.exists("data/notification_history.json"):
                with open("data/notification_history.json", "r") as f:
                    self.history = json.load(f)
        except Exception as e:
            print(f"Error loading notification history: {e}")
            self.history = []

    def generate_tutor_access_code(self, student_code):
        """
        Generate a unique access code for tutors
        """
        timestamp = datetime.now().strftime("%Y%m%d")
        code_base = f"{student_code}{timestamp}"
        code_hash = hashlib.md5(code_base.encode()).hexdigest()[:8].upper()
        return code_hash
