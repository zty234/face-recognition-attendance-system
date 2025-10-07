from django import forms
from .models import User

# 创建注册表单

class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="确认密码")

    class Meta:
        model = User
        fields = ['username', 'password']  # 仅包含用户需要输入的字段
    
    # 验证两次密码是否正确
    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            # raise forms.ValidationError("密码不一致")
            self.add_error('password_confirm', "两次输入的密码不一致")
        
        return cleaned_data
    
    # 保存用户时加密密码
    def save(self, commit = True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = User.STUDENT
        if commit:
            user.save()

        return user

# 教师表单继承学生表单
class TeacherRegistrationForm(StudentRegistrationForm):
    def save(self, commit = True):
        user = super().save(commit=False)
        user.role = User.TEACHER

        if commit:
            user.save()

        return user
    

class UserPhotoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['photo']
        labels = {
            'photo': 'Upload your photo'
        }

        widgets = {
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }