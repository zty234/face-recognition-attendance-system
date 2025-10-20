[中文版本 🇨🇳](./README.zh.md)
# Face Recognition Attendance System

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.x-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This is a real-time face recognition attendance system developed with Python, Django, and the `face_recognition` library. The project uses a client-server architecture. The server is deployed in a WSL (Ubuntu) environment, while the client utilizes a Windows-based camera for real-time video stream transmission.

**Compared to official tutorials or other projects using `face_recognition`, this project solves the difficult installation and environment configuration issues on Windows. You can compile and run it directly using VS Code or PyCharm without needing to install Visual Studio.**

---

## Core Features

-   **Real-time Face Recognition**: Performs real-time face detection and identification via webcam.
-   **Web Management Interface**: Provides features for user registration, face photo uploads, and viewing attendance records.
-   **Client-Server Architecture**: Flexible deployment by separating video capture (client) from logic processing (server).
-   **WebSocket Real-time Communication**: Low-latency, efficient video frame transmission between client and server using WebSocket.

---

## Tech Stack

-   **Backend**: Python, Django
-   **Face Recognition**: `face_recognition` (based on dlib)
-   **Real-time Communication**: WebSocket
-   **Frontend**: HTML, CSS, JavaScript
-   **Runtime Environment**:
    -   **Server**: WSL (Ubuntu)
    -   **Client**: Windows

---

## System Architecture

This system is designed with two core components:

1.  **Server**:
    -   Runs in the **WSL (Ubuntu)** environment.
    -   Uses the **Django** framework to handle all backend logic, including user authentication, database management, and face data comparison.
    -   Receives video frames from the client via WebSocket.
    -   Processes and recognizes faces, and records attendance data.

2.  **Client**:
    -   A Python script (`send_frame.py`) running on **Windows**.
    -   Uses the OpenCV library to access the local camera.
    -   Captures video frames and sends them to the server in real-time over a WebSocket connection.

---

## Project Structure

```
student_attendance/
├── client_windows/
│   └── send_frame.py         # Windows client: Captures and sends camera frames
├── server_wsl/
│   ├── django_app/           # Django project core code
│   └── flask_app/            # (Deprecated) Old Flask version, kept 
├── .gitignore                # Git ignore file configuration
└── README.md                 # Project description file (this file)
```

---

## Installation and Usage

Before you begin, ensure you have Python, pip, and Git installed. If you use Anaconda, ensure Conda is installed.

### 1. Server-side Setup (in WSL)

```bash
# Clone the repository
git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
cd student_attendance/server_wsl/django_app
```

**Choose your environment management method:**

**Method A: Using venv (Native Python)**

```bash
# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate
```

**Method B: Using Anaconda/Conda**

```bash
# If you haven't created an environment, create one first (replace face-rec with your env name)
# conda create --name face-rec python=3.9

# Activate the Conda environment
conda activate your-environment-name
```

---
**Continue with the following steps:**

```bash
# Install all dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Start the Django server
# Note: Use 0.0.0.0 to allow the Windows client to access the service running in WSL
python manage.py runserver 0.0.0.0:8000
```

---

## Usage Flow

1.  **Start the Server**: First, start the Django server in WSL.
2.  **User Registration**: Access the Django website (e.g., `http://<your-wsl-ip>:8000`), register a new user, and upload a clear, frontal photo. The server will automatically save the face data to the `media/face_images` folder.
3.  **Course Registration**: Log in to the Django admin panel as a superuser to create courses, course sessions, and enroll participants.
4.  **Start the Client**: Run the `send_frame.py` script on Windows. The local camera will be activated.
5.  **Begin Attendance**: The client will stream the camera feed to the server. When a registered face appears in front of the camera, the system will recognize it and log the attendance.

---

## Notes

-   **`media/face_images` Folder**: This folder was used to store user-uploaded face images. For privacy and security, it has been added to `.gitignore` and will not be uploaded to the GitHub repository.
-   **`flask_app` Folder**: This is an early, deprecated Flask implementation, kept only for reference from the development process.