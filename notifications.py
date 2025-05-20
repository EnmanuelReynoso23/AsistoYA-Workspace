import requests
import json
from datetime import datetime
from twilio.rest import Client

class NotificationManager:
    def __init__(self, api_url, api_key, twilio_sid=None, twilio_token=None, twilio_phone=None):
        self.api_url = api_url
        self.api_key = api_key
        self.history = []
        self.twilio_client = None
        if twilio_sid and twilio_token and twilio_phone:
            self.twilio_client = Client(twilio_sid, twilio_token)
            self.twilio_phone = twilio_phone

    def send_notification(self, phone_number, template, student_name):
        message = template.replace("{{Nombre}}", student_name)
        payload = {
            "phone_number": phone_number,
            "message": message
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        response = requests.post(self.api_url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            self.log_notification(phone_number, message)
        else:
            print(f"Failed to send notification: {response.status_code} - {response.text}")

    def send_sms(self, phone_number, message):
        if self.twilio_client:
            try:
                message = self.twilio_client.messages.create(
                    body=message,
                    from_=self.twilio_phone,
                    to=phone_number
                )
                self.log_notification(phone_number, message.body)
            except Exception as e:
                print(f"Failed to send SMS: {e}")
        else:
            print("Twilio client is not configured.")

    def log_notification(self, phone_number, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({
            "phone_number": phone_number,
            "message": message,
            "timestamp": timestamp
        })

    def get_notification_history(self):
        return self.history
