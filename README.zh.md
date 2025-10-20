# 人脸识别考勤系统 (Face Recognition Attendance System)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.x-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

这是一个基于 Python Django 和 `face_recognition` 库开发的实时人脸识别考勤系统。项目采用客户端/服务器架构，服务器部署在 WSL (Ubuntu) 环境，而客户端则利用 Windows 端的摄像头进行实时视频流传输。

**相较于官方教程或者其他使用`face_recognition`的项目，本项目解决了Windows系统下不容易安装和配置环境的问题。可以直接使用VS code或者Pycharm编译运行不用再安装Visual Studio。**

---

## 核心功能

- **实时人脸识别**：通过摄像头实时进行人脸检测与身份识别。
- **Web管理后台**：提供用户注册、人脸照片上传和考勤记录查看等功能。
- **客户端/服务器架构**：分离了视频采集（客户端）和逻辑处理（服务器），部署灵活。
- **WebSocket 实时通信**：客户端与服务器之间使用 WebSocket 高效传输视频帧，延迟低。

---

## 技术栈

- **后端**: Python, Django
- **人脸识别**: `face_recognition` (基于 dlib)
- **实时通信**: WebSocket
- **前端**: HTML, CSS, JavaScript
- **运行环境**:
  - **服务器**: WSL (Ubuntu)
  - **客户端**: Windows

---

## 系统架构

本系统被设计为两个核心部分：

1.  **服务器 (Server)**:
    -   运行在 **WSL (Ubuntu)** 环境中。
    -   使用 **Django** 框架处理所有后端逻辑，包括用户认证、数据库管理和人脸数据比对。
    -   通过 WebSocket 接收来自客户端的视频帧。
    -   处理和识别人脸，并记录考勤数据。

2.  **客户端 (Client)**:
    -   一个运行在 **Windows** 上的 Python 脚本 (`send_frame.py`)。
    -   使用 OpenCV 库调用本地摄像头。
    -   捕获视频帧，并通过 WebSocket 连接实时发送给服务器。

---

## 项目结构

```
student_attendance/
├── client_windows/
│   └── send_frame.py         # Windows 客户端：负责捕获并发送摄像头画面
├── server_wsl/
│   ├── django_app/           # Django 项目核心代码
│   └── flask_app/            # (已弃用) 旧的 Flask 版本，保留参考
├── .gitignore                # Git 忽略文件配置
└── README.md                 # 项目说明文件
```

---

## 安装与启动

在开始之前，请确保你已经安装了 Python, pip 和 Git。如果你使用 Anaconda，请确保已安装 Conda。

### 1. 服务器端配置 (在 WSL 中)

```bash
# 克隆仓库
git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
cd student_attendance/server_wsl/django_app
```

**选择你的环境管理方式：**

**方式 A: 使用 venv (Python 原生)**
```bash
# 创建并激活 Python 虚拟环境
python3 -m venv venv
source venv/bin/activate
```

**方式 B: 使用 Anaconda/Conda**
```bash
# 如果还未创建环境，请先创建 (将 face-rec 替换为你的环境名)
# conda create --name face-rec python=3.9

# 激活 Conda 环境
conda activate your-environment-name
```

---
**继续以下步骤：**

```bash
# 安装所有依赖
pip install -r requirements.txt

# 进行数据库迁移
python manage.py migrate

# 启动 Django 服务器
# 注意：使用 0.0.0.0 是为了让 Windows 端的客户端可以访问到 WSL 中的服务
python manage.py runserver 0.0.0.0:8000
```

---

## 使用流程

1.  **启动服务**: 首先在 WSL 中启动 Django 服务器。
2.  **用户注册**: 访问 Django 网站 (例如 `http://<your-wsl-ip>:8000`)，注册新用户并上传一张清晰的正面照片。服务器会自动将人脸数据保存在 `known_faces` 文件夹中。
3. **课程注册**: 进入django admin, 以superuser身份登录并且创建课程和课表以及参与人员
4.  **启动客户端**: 在 Windows 上运行 `send_frame.py` 脚本，本地摄像头将被激活。
5.  **开始考勤**: 客户端会将摄像头画面实时传输到服务器。当已注册的面孔出现在摄像头前时，系统会完成识别并记录考勤。

---

## 注意事项

- **`known_faces` 文件夹**: 此文件夹用于存储用户上传的人脸图像。出于用户隐私和安全考虑，它已被添加到 `.gitignore` 中，不会被上传到 GitHub 仓库。
- **`flask_app` 文件夹**: 这是一个早期的、已弃用的 Flask 版本实现，仅作为开发过程的参考保留。