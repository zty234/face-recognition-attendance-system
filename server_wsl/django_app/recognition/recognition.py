import face_recognition
import numpy as np
import cv2
import os
import threading
from django.utils import timezone
from .models import User, AttendanceRecord, Course, CourseSession
from datetime import datetime, timedelta

# 加锁，防止摄像头识别同时更新数据库导致线程崩溃
face_data_lock = threading.Lock()
recently_marked_lock = threading.Lock()

# 新建face_encodings 和 face_names数组
known_face_encodings = []
known_face_names = []


# 获取当前recognition.py的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print("BASE_DIR", BASE_DIR)
# construct abspath of known_faces
known_dir = os.path.join(BASE_DIR, 'known_faces')
print("knwon_dir", known_dir)

def load_known_faces():
    global known_face_encodings, known_face_names

    # 清空来完成refresh
    # known_face_names.clear()
    # known_face_encodings.clear()
    with face_data_lock:
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
                if len(face_locations) == 0:
                    print(f"[Warning]No face founded in {filename}")
                    continue

                face_encodings = face_recognition.face_encodings(image, face_locations)
                if len(face_encodings) == 0:
                    print(f"[Warning]Fail to encode faces in {filename}")
                    continue

                # 存入列表
                known_face_encodings.extend(face_encodings)
    
    print(f"load {len(known_face_names)} faces")

# 注册时添加单个face
def load_new_face(name, filepath):
    with face_data_lock:
        try:
            image = face_recognition.load_image_file(filepath)
            face_locations = face_recognition.face_locations(image)
            if len(face_locations) == 0:
                print(f"[Warning]No face founded in {name}")
                return False
            
            face_encodings = face_recognition.face_encodings(image, face_locations)
            if len(face_encodings) == 0:
                print(f"[Warning]Fail to encode faces in {name}")
                return False
            
            known_face_names.append(name)
            known_face_encodings.extend(face_encodings)
            
            print(f"Successfully add {name}")
            return True
        
        except Exception as e:
            print(f"[Error] Exception during loading: {e}")
            return False


TOLERANCE = 0.6
DISTANCE_THRESHOLD = 0.55

now = timezone.now()
recently_marked = {}

# 清理10秒前的识别记录
with recently_marked_lock:
    to_delete = [name for name, t in recently_marked.items() if (now - t).total_seconds() > 10]
    for name in to_delete:
        del recently_marked[name]


# 视频人脸匹配
def face_match(frame):
    with face_data_lock:
        # BGR转RGB满足face_recognition
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 检测视频人脸位置
        face_locations = face_recognition.face_locations(frame_rgb)
        
        # 提取视频人脸特征编码
        face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)

        results = []

        # 遍历视频人脸编码并且和已知编码匹配
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, TOLERANCE)

            # 计算距离(match返回多个True时选最小距离的人脸)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            min_face_distance_index = np.argmin(face_distances) # 0, 1, 2
            min_face_distance = face_distances[min_face_distance_index]

            name = "Unknown"
            status = "Fail"

            if matches[min_face_distance_index] and min_face_distance < DISTANCE_THRESHOLD:
                name = known_face_names[min_face_distance_index]

                attendance = mark_once(name)
                status = attendance['status']

            results.append({"name": name, "top": top, "right": right, "bottom": bottom, "left": left, "status":status})

        return results



# 每节课每个用户只打卡一次
def mark_once(name):

    # 获取当前时间
    now = timezone.now()

    # 获取当前用户
    try:
        user = User.objects.get(username = name)
    except User.DoesNotExist:
        return {'status': 'Fail'}
    
    # 查找该用户当前正在上的课程
    current_classes = CourseSession.objects.filter(
        start_time__lte = now,
        end_time__gte = now,
        course__students = user
    )

    if not current_classes.exists():
        return {'status': 'Fail'}
    
    # 只能上一门课
    current_class = current_classes.first()

    # 判断是否已经打过卡
    already_marked = AttendanceRecord.objects.filter(user = user, course_session = current_class).exists()
    if already_marked:
        with recently_marked_lock:
            if name in recently_marked:
                pass
            else:
                return {'status': 'Already marked'}

    # 第一次打卡流程, 判断是否迟到
    current_class_start = current_class.start_time
    current_class_end = current_class.end_time
    on_time_deadline = current_class_start + timezone.timedelta(minutes=10)  # 10 mins内不算late
    early_time = current_class_start - timezone.timedelta(minutes=10) # 提前10 mins打卡

    if now < early_time:
        status_str = 'Too early'
    elif now <= on_time_deadline:
        status_str = 'Present'
    elif now <= current_class_end:
        status_str = 'Late'
    else:
        status_str = 'Absent'
    
    # 保证不给已经打过卡的人打卡(因为上面有pass所以10秒内打过卡的可能会再次出现在这里)
    if not already_marked:
        AttendanceRecord.objects.create(
            user = user,
            attendance_time = now,
            course_session = current_class,
            status = status_str
        )

    with recently_marked_lock:
        # 更新recently_marked
        recently_marked[name] = now

    return {'status': status_str}


# 课程结束后自动设置Absent
def auto_mark_absent():
    now = timezone.now()
    one_min_ago = now - timedelta(minutes=1)

    ended_classes = CourseSession.objects.filter(
        end_time__lte = now, end_time__gte = one_min_ago
    )

    for ended_class in ended_classes:
        students = ended_class.course.students.all()
        for student in students:
            if not AttendanceRecord.objects.filter(user = student, course_session = ended_class).exists():
                AttendanceRecord.objects.create(
                    user = student,
                    course_session = ended_class,
                    attendance_time = ended_class.end_time,
                    status = 'Absent'
                )
    
    
