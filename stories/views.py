from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Story, Chapter
from .forms import StoryForm, ChapterForm
import os
import docx
from django.conf import settings

@login_required
def admin_dashboard(request):
    stories = Story.objects.all().order_by('-id')
    return render(request, 'admin/dashboard.html', {'stories': stories})

@login_required
def admin_add_story(request):
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save()
            messages.success(request, "Đã thêm truyện thành công!")

            # Xử lý upload file (txt/docx)
            uploaded_file = request.FILES.get('story_file')
            if uploaded_file:
                file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', uploaded_file.name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, 'wb+') as dest:
                    for chunk in uploaded_file.chunks():
                        dest.write(chunk)

                # Xử lý file và tách chương
                chapters_data = []
                if file_ext == '.txt':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    chapters_data = parse_chapters_from_text(content)
                elif file_ext == '.docx':
                    doc = docx.Document(file_path)
                    full_text = []
                    for para in doc.paragraphs:
                        full_text.append(para.text)
                    content = '\n'.join(full_text)
                    chapters_data = parse_chapters_from_text(content)

                # Lưu các chương vào DB
                for ch_data in chapters_data:
                    Chapter.objects.create(
                        story=story,
                        chapter_number=ch_data['number'],
                        title=ch_data['title'],
                        content=ch_data['content']
                    )
                messages.success(request, f"Đã import {len(chapters_data)} chương từ file.")

            return redirect('admin_dashboard')
    else:
        form = StoryForm()
    return render(request, 'admin/add_story.html', {'form': form})

# Helper function để tách chương từ text
def parse_chapters_from_text(text): 
    chapters = []
    lines = text.split('\n')
    current_chapter = None
    current_content = []

    for line in lines:
        line = line.strip()
        if line.lower().startswith('chương') or line.lower().startswith('chapter'):
            if current_chapter:
                chapters.append(current_chapter)
            # Tạo chương mới
            try:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    title = parts[1].strip()
                else:
                    title = ""
                current_chapter = {
                    'number': len(chapters) + 1,
                    'title': title,
                    'content': ""
                }
            except:
                current_chapter = {
                    'number': len(chapters) + 1,
                    'title': line,
                    'content': ""
                }
            current_content = []
        elif current_chapter:
            current_content.append(line)
        else:
            # Bỏ qua text trước chương đầu tiên
            pass

    if current_chapter:
        current_chapter['content'] = '\n'.join(current_content)
        chapters.append(current_chapter)

    return chapters
def home(request):
    """Trang chủ hiển thị danh sách truyện"""
    stories = Story.objects.all().order_by('-id')
    return render(request, 'home.html', {'stories': stories})

def story_detail(request, story_id):
    """Trang chi tiết truyện"""
    story = get_object_or_404(Story, id=story_id)
    chapters = story.chapters.all()

    # Xử lý mật khẩu
    if story.is_locked():
        if request.method == 'POST':
            password = request.POST.get('password')
            if password == story.password:
                # Lưu vào session để không phải nhập lại
                request.session[f'story_{story.id}_unlocked'] = True
                return redirect('story_detail', story_id=story.id)
            else:
                messages.error(request, "Sai mật khẩu!")
        # Kiểm tra session
        if not request.session.get(f'story_{story.id}_unlocked'):
            return render(request, 'story_locked.html', {'story': story})

    return render(request, 'story_detail.html', {
        'story': story,
        'chapters': chapters
    })

def read_chapter(request, story_id, chapter_number):
    """Trang đọc chương"""
    story = get_object_or_404(Story, id=story_id)
    chapter = get_object_or_404(Chapter, story=story, chapter_number=chapter_number)

    # Kiểm tra mật khẩu
    if story.is_locked():
        if not request.session.get(f'story_{story.id}_unlocked'):
            return redirect('story_detail', story_id=story.id)

    # Lấy chương trước và sau
    prev_chapter = Chapter.objects.filter(story=story, chapter_number=chapter_number - 1).first()
    next_chapter = Chapter.objects.filter(story=story, chapter_number=chapter_number + 1).first()

    return render(request, 'read_chapter.html', {
        'story': story,
        'chapter': chapter,
        'prev_chapter': prev_chapter,
        'next_chapter': next_chapter
    })
    
def get_password_guide(request):
    """Trang hướng dẫn lấy mật khẩu"""
    return render(request, 'get_password_guide.html')