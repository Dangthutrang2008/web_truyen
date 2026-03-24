from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import RegisterForm, LoginForm
from stories.models import Story

def user_register(request):
    """Đăng ký tài khoản mới"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Đăng nhập ngay sau khi đăng ký
            login(request, user)
            messages.success(request, f'Chào mừng {user.username}! Đăng ký thành công.')
            return redirect('home')
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    """Đăng nhập"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            try:
                # Tìm user bằng email
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
                
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Chào mừng trở lại, {user.username}!')
                    return redirect('home')
                else:
                    messages.error(request, 'Email hoặc mật khẩu không đúng.')
            except User.DoesNotExist:
                messages.error(request, 'Email không tồn tại.')
        else:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    """Đăng xuất"""
    logout(request)
    messages.success(request, 'Đã đăng xuất thành công!')
    return redirect('home')

@login_required
def user_profile(request):
    """Trang hồ sơ cá nhân"""
    favorite_stories = []
    if hasattr(request.user, 'profile'):
        favorite_stories = request.user.profile.favorite_stories.all()
    
    context = {
        'user': request.user,
        'favorite_stories': favorite_stories,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def toggle_favorite(request, story_id):
    """Thêm/xóa truyện yêu thích"""
    try:
        story = Story.objects.get(id=story_id)
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            
            if story in profile.favorite_stories.all():
                profile.favorite_stories.remove(story)
                messages.success(request, f'Đã xóa "{story.title}" khỏi danh sách yêu thích')
            else:
                profile.favorite_stories.add(story)
                messages.success(request, f'Đã thêm "{story.title}" vào danh sách yêu thích')
        else:
            messages.error(request, 'Không tìm thấy hồ sơ người dùng.')
    except Story.DoesNotExist:
        messages.error(request, 'Truyện không tồn tại.')
    
    return redirect('story_detail', story_id=story_id)