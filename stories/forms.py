from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from stories.models import Chapter, Story

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(label='Tên đăng nhập', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Mật khẩu', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Xác nhận mật khẩu', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email đã được sử dụng')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Tên đăng nhập đã tồn tại')
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email', 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@email.com'})
    )
    password = forms.CharField(
        label='Mật khẩu', 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )
class StoryForm(forms.ModelForm):
    story_file = forms.FileField(required=False, label="Upload file truyện (txt/docx)")

    class Meta:
        model = Story
        fields = ['title', 'author', 'description', 'cover', 'password']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['story', 'chapter_number', 'title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 15, 'style': 'font-family: monospace;'}),
        }