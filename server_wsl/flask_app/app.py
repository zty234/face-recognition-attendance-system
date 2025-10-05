import face_recognition
from flask import Flask, jsonify, request 
import numpy as np
import cv2

from recognition import load_known_faces, face_match

app = Flask(__name__)

# 加载已知图像
load_known_faces()

@app.route("/recognize", methods=["POST"])
def recognize():
    if  "image" not in request.files:
        return jsonify({"error":"No image received"}), 400
    
    # 读文件
    file = request.files["image"]

    # 二进制转numpy数组
    img_array = np.frombuffer(file.read(), np.uint8)

    # numpy数组转三通道
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    result = face_match(frame)

    return jsonify({"faces":result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)