import os
import shutil
import platform
import subprocess
import requests

class Installer:
    def __init__(self, app_name, version):
        self.app_name = app_name
        self.version = version
        self.os_type = platform.system()

    def create_installer(self):
        if self.os_type == "Windows":
            self.create_windows_installer()
        elif self.os_type == "Linux":
            self.create_linux_installer()
        elif self.os_type == "Darwin":
            self.create_mac_installer()
        else:
            raise Exception("Unsupported OS")

    def create_windows_installer(self):
        # Create a Windows installer using Inno Setup
        script = f"""
        [Setup]
        AppName={self.app_name}
        AppVersion={self.version}
        DefaultDirName={{pf}}\\{self.app_name}
        DefaultGroupName={self.app_name}
        OutputBaseFilename={self.app_name}_Installer

        [Files]
        Source: "dist\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs
        """
        with open("installer.iss", "w") as file:
            file.write(script)
        subprocess.run(["iscc", "installer.iss"])

    def create_linux_installer(self):
        # Create a Linux installer using makeself
        subprocess.run(["makeself", "--notemp", "dist", f"{self.app_name}_Installer.run", self.app_name, "./install.sh"])

    def create_mac_installer(self):
        # Create a macOS installer using pkgbuild
        subprocess.run(["pkgbuild", "--root", "dist", "--identifier", f"com.example.{self.app_name}", "--version", self.version, f"{self.app_name}_Installer.pkg"])

    def check_for_updates(self):
        # Check for updates from a remote server
        response = requests.get("https://example.com/updates")
        if response.status_code == 200:
            update_info = response.json()
            if update_info["version"] > self.version:
                self.download_update(update_info["url"])

    def download_update(self, update_url):
        # Download the update file
        response = requests.get(update_url, stream=True)
        with open("update.zip", "wb") as file:
            shutil.copyfileobj(response.raw, file)
        self.install_update("update.zip")

    def install_update(self, update_file):
        # Install the update
        shutil.unpack_archive(update_file, "update")
        subprocess.run(["python", "update/install.py"])

if __name__ == "__main__":
    installer = Installer("Asisto Ya", "1.0.0")
    installer.create_installer()
    installer.check_for_updates()
