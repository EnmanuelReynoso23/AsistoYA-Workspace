import requests
import json
from datetime import datetime

class NotificationManager:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
        self.history = []

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

    def log_notification(self, phone_number, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({
            "phone_number": phone_number,
            "message": message,
            "timestamp": timestamp
        })

    def get_notification_history(self):
        return self.history
