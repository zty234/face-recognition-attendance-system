from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    # 不自己定义username, 直接继承父类
    #user_name = models.CharField(max_length=50, unique=True)

    # 定义学生和教师
    STUDENT = 'student'
    TEACHER = 'teacher'
    ROLE_CHOICES = [
        (STUDENT, 'student'),
        (TEACHER, 'teacher')
    ]

    photo_path = models.CharField(max_length=200)
    register_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)

    #USERNAME_FIELD = "user_name"  # 因为自定义了user_name, django默认的是username
    #REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.username}({self.role}): {self.register_at}"
    
class Course(models.Model):
    name = models.CharField(max_length=50)

    # Many to Many
    students = models.ManyToManyField(User, related_name="courses")

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="taught_courses")
    
    def __str__(self):
        return self.name

    
class CourseSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.course.name} : {self.start_time} - {self.end_time}"
    
    def course_name(self):
        return self.course.name

class AttendanceRecord(models.Model):
    attendance_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE) # set a foreignkey related to user, 如果User删除那么user中对应的字段也删除
    course_session = models.ForeignKey(CourseSession, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='Present') # Present Late Absent

    def __str__(self):
        return f"{self.user.username} - {self.course_session.course.name} - {self.attendance_time.strftime('%Y-%m-%d %H:%M') } - {self.status}"
