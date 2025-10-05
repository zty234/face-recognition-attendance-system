import face_recognition
import numpy as np
import cv2
import os

# 新建face_encodings 和 face_names数组
known_face_encodings = []
known_face_names = []


# 读取已存在的人脸
known_dir = "./known_faces"

def load_known_faces():
    for filename in os.listdir(known_dir):
        # 提取图片人脸对应的名称
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            name = os.path.splitext(filename)[0]
            known_face_names.append(name)
        
            # 提取人脸图片
            image_path = os.path.join(known_dir, filename)
            image = face_recognition.load_image_file(image_path)

            # 提取图片人脸的特征编码
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)

            # 存入列表
            known_face_encodings.extend(face_encodings)
    
    print(f"load {len(known_face_names)} faces")

# 视频人脸匹配
def face_match(frame):

    # BGR转RGB满足face_recognition
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 检测视频人脸位置
    face_locations = face_recognition.face_locations(frame_rgb)
    
    # 提取视频人脸特征编码
    face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)

    results = []

    # 遍历视频人脸编码并且和已知编码匹配
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)

        # 计算距离(match返回多个True时选最小距离的人脸)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        min_face_distance_index = np.argmin(face_distances) # 0, 1, 2
        min_face_distance = face_distances[min_face_distance_index]

        name = "Unknown"

        if matches[min_face_distance_index] and min_face_distance < 0.55:
            name = known_face_names[min_face_distance_index]

        results.append({"name": name, "top": top, "right": right, "bottom": bottom, "left": left})

    return results

