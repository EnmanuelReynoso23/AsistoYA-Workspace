class Settings:
    def __init__(self):
        self.recognition_threshold = 0.5
        self.class_schedules = {}
        self.network_settings = {
            "proxy": None,
            "ports": []
        }
        self.storage_paths = {
            "photos": "./photos",
            "messages": "./messages"
        }

    def set_recognition_threshold(self, threshold):
        self.recognition_threshold = threshold

    def add_class_schedule(self, class_name, schedule):
        self.class_schedules[class_name] = schedule

    def set_network_settings(self, proxy, ports):
        self.network_settings["proxy"] = proxy
        self.network_settings["ports"] = ports

    def set_storage_paths(self, photos_path, messages_path):
        self.storage_paths["photos"] = photos_path
        self.storage_paths["messages"] = messages_path

    def get_recognition_threshold(self):
        return self.recognition_threshold

    def get_class_schedules(self):
        return self.class_schedules

    def get_network_settings(self):
        return self.network_settings

    def get_storage_paths(self):
        return self.storage_paths
