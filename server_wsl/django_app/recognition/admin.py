from django.contrib import admin
from .models import User, AttendanceRecord, Course, CourseSession
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.

'''''
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'photo_path', 'register_at')
    search_fields = ('username',)
    list_filter = ('register_at',)
'''

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'role', 'photo', 'register_at', 'is_staff', 'is_superuser')
    list_filter = ('role', 'register_at', 'is_staff', 'is_superuser')
    search_fields = ('username',)
    ordering = ('-register_at',)

    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role', 'photo',)}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'photo',)}),
    )

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('students',)

@admin.register(CourseSession)
class CourseSessionAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'start_time', 'end_time')
    list_filter = ('course__name', 'start_time')
    search_fields = ('course__name',)

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('username', 'attendance_time', 'course_session_name', 'status')
    list_filter = ('status', 'attendance_time', 'course_session__course__name')
    search_fields = ('user__username', 'course_session__course__name')
    def username(self, obj):
        return obj.user.username
    username.short_description = "User"

    def course_session_name(self, obj):
        return f"{obj.course_session.course.name} ({obj.course_session.start_time.strftime('%Y-%m-%d %H:%M')})"
    course_session_name.short_description = "Course Session"
