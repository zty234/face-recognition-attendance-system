from django.shortcuts import render, redirect
from . import recognition
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponse, HttpRequest
from .models import User, AttendanceRecord, Course, CourseSession
from django.contrib.auth.decorators import login_required
from .forms import StudentRegistrationForm, TeacherRegistrationForm, UserPhotoForm
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
import os

# Create your views here.
'''
@login_required
def upload_face(request:HttpRequest):
    if request.method == 'POST':
        photo = request.FILES.get('photo')

        if not photo:
            return HttpResponse("photo cannot be empty", status = 400)
        
        username = request.user.username
        # 提取文件类型
        _, file_extension = os.path.splitext(photo.name)

        # 转小写
        file_extension = file_extension.lower()

        # 格式检查
        allowed_extensions = ['.jpg', '.png', '.jpeg', '.webp']
        if file_extension not in allowed_extensions:
            return HttpResponse(f"不支持此格式！请选择以下类型：{allowed_extensions}", status = 400)
        

        folder_path = os.path.join(settings.BASE_DIR, 'recognition/known_faces')
        os.makedirs(folder_path, exist_ok=True) # 不存在创建，存在不创建

        file_path = os.path.join(folder_path, f"{username}{file_extension}")
        # 以二进制写入模式(wb)打开文件, 准备保存
        with open(file_path, 'wb') as f:
            # 大文件截成chunks处理节省资源
            for chunk in photo.chunks():
                f.write(chunk)

        # User.objects.create(user_name = name, photo_path = file_path)

        # 更新photo_path
        try:
            user_obj = User.objects.get(username = username)
            user_obj.photo_path = file_path
            user_obj.save()

        except User.DoesNotExist:
            #return HttpResponse("用户不存在, 请先注册", status = 400)
            messages.error(request, "用户不存在, 请先注册")
            return redirect('register_student')
        # 每次创建就刷新
        # recognition.load_known_faces()

        success = recognition.load_new_face(username, file_path)
        if not success:
            #return HttpResponse("Face Recognition Failed", status = 400)
            messages.error(request, "Face Loading Failed")
            return redirect('student_dashboard')
        
        #return HttpResponse("Successfully uploaded face!")
        messages.success(request, "Successfully upload face")
        return redirect('student_dashboard')
    
    # if request.method == 'GET':
    return render(request, 'upload_face.html')
'''
@login_required
def upload_face(request: HttpRequest):
    # We are updating the currently logged-in user, so we pass `instance=request.user`
    if request.method == 'POST':
        # Bind the uploaded data to the form
        form = UserPhotoForm(request.POST, request.FILES, instance=request.user)
        
        # form.is_valid() handles all the validation automatically
        if form.is_valid():
            # form.save() automatically saves the photo to the `media/face_images`
            # directory and updates the `photo` field on the user model.
            user = form.save()

            # Get the path of the newly saved photo
            file_path = user.photo.path
            username = user.username

            # Now, load this new face into your recognition system
            success = recognition.load_new_face(username, file_path)

            if success:
                messages.success(request, "Successfully uploaded and loaded face!")
            else:
                messages.error(request, "Face was uploaded but could not be recognized. Please use a clear, frontal photo.")
            
            return redirect('student_dashboard')
    
    # For a GET request, just display an empty form
    else:
        form = UserPhotoForm(instance=request.user)

    return render(request, 'upload_face.html', {'form': form})

@login_required
def record(request:HttpRequest):
    user = request.user

    if not user.photo.path:
        messages.warning(request, "未上传图像")
        return redirect('student_dashboard')
    
    records = AttendanceRecord.objects.select_related('user').filter(user = user).order_by('-attendance_time')

    return render(request, 'student_record.html', {'records':records})

@login_required
def teacher_view_attendance(request:HttpRequest):
    user = request.user

    if user.role != 'teacher':
        messages.error(request, "You are not authorized to view this page")
        return redirect('student_dashboard')
    
    # 获取老师所教的所有课
    teacher_courses = Course.objects.filter(teacher = user)

    records = AttendanceRecord.objects.select_related('course_session__course').filter(course_session__course__in = teacher_courses).order_by('-attendance_time')

    return render(request, 'teacher_view_attendance.html', {'records': records})

# 注册逻辑
def register_student(request:HttpRequest):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Successfully register as a student!")
            return redirect('login')
    
    else:
        form = StudentRegistrationForm()

    return render(request, 'register.html', {'form' : form, 'title': 'Student Register'})

def register_teacher(request:HttpRequest):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Successfully register as a teacher!")
            return redirect('login')
    
    else:
        form = TeacherRegistrationForm()

    return render(request, 'register.html', {'form': form, 'title': 'Teacher Register'})

@login_required
def student_dashboard(request:HttpRequest):
    return render(request, 'student_dashboard.html', {
        'user':request.user,
        })

@login_required
def teacher_dashboard(request:HttpRequest):
    return render(request, 'teacher_dashboard.html',{
        'user': request.user
    })

class RoleBasedLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        user = self.request.user
        if user.role == 'teacher':
            return reverse_lazy('teacher_dashboard')
        else:
            return reverse_lazy('student_dashboard')
    
        
        