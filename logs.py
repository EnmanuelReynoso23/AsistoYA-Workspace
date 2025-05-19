import logging
from datetime import datetime

class LogManager:
    def __init__(self, log_file):
        self.log_file = log_file
        logging.basicConfig(filename=self.log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

    def log_event(self, event):
        logging.info(event)

    def view_logs(self):
        with open(self.log_file, 'r') as file:
            logs = file.readlines()
        return logs

    def export_logs(self, export_file):
        with open(self.log_file, 'r') as file:
            logs = file.read()
        with open(export_file, 'w') as file:
            file.write(logs)
