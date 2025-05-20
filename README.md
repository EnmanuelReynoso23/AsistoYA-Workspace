# Asisto Ya

## Project Description and Overview

Asisto Ya is a desktop application designed to capture attendance using Computer Vision. It integrates OpenCV or YOLOv8 for facial detection and/or recognition. The application includes various modules and features to meet the needs of teachers, parents, and administrators.

### Key Features

- **Attendance Capture**: Uses Computer Vision for facial detection and recognition.
- **Camera Configuration**: Supports webcam or other sources with automatic lighting/contrast adjustment.
- **Teacher Interface**: Real-time classroom view with detected faces, quick buttons for starting, pausing, and ending attendance sessions, and a list of enrolled students with their attendance status.
- **WhatsApp Notifications**: Connects to the WhatsApp Business API or Twilio for automatic message sending with customizable templates and notification history.
- **User and Role Management**: Secure login for teachers, administrators, and optional secretarial staff with granular permissions.
- **Database and Storage**: SQL database (SQLite or MySQL) for storing student information, attendance records, and notification settings, with backup and restoration options.
- **Reports and Export**: Generates daily, weekly, and monthly reports, exports attendance lists to Excel/PDF, and provides basic attendance graphs.
- **Settings and Customization**: Manages recognition threshold, class schedules, network settings, and storage paths.
- **Security and Privacy**: Encrypts sensitive data, enforces secure login and optional two-factor authentication, and implements data retention policies.
- **Logs and Auditing**: Logs important events, provides log viewing and export for diagnostics.
- **Installer and Updates**: Creates an installer package for Windows/Linux/macOS and implements an automatic update system.
- **Help and Support**: Includes a user manual and support information, with an "About" section for version and contact details.

## Setting Up the Development Environment

To set up the development environment for Asisto Ya, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/EnmanuelReynoso23/AsistoYA-Workspace.git
   cd AsistoYA-Workspace
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**:
   ```bash
   python database.py --setup
   ```

## Running the Application

To run the application, use the following command:

```bash
python main.py
```

## Running the Application with ttkbootstrap

To run the application with `ttkbootstrap`, use the following command:

```bash
python main.py
```

## Contributing to the Project

We welcome contributions to Asisto Ya! To contribute, follow these steps:

1. **Fork the repository** on GitHub.
2. **Clone your forked repository** to your local machine.
3. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b my-feature-branch
   ```
4. **Make your changes** and commit them with descriptive messages.
5. **Push your changes** to your forked repository:
   ```bash
   git push origin my-feature-branch
   ```
6. **Create a pull request** on the original repository.

Please ensure your code follows our coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
