from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Story, Chapter
from .forms import StoryForm, ChapterForm
import os
import docx
from django.conf import settings
import re

ADMIN_PASSWORD = "dangthutrang123456"  # Đổi thành mật khẩu bạn muốn

def admin_dashboard(request):
    """Dashboard admin - mỗi lần vào đều phải nhập mật khẩu"""
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == ADMIN_PASSWORD:
            # Không lưu session, chỉ cho xem dashboard trong request này
            stories = Story.objects.all().order_by('-id')
            return render(request, 'admin/dashboard.html', {'stories': stories})
        else:
            messages.error(request, 'Mật khẩu không đúng!')
            return render(request, 'admin/admin_login.html')
    
    # GET request: hiển thị form nhập mật khẩu
    return render(request, 'admin/admin_login.html')

def admin_add_story(request):
    """Thêm truyện mới"""
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save()
            messages.success(request, f"Đã thêm truyện '{story.title}' thành công!")

            # Xử lý upload file
            uploaded_file = request.FILES.get('story_file')
            if uploaded_file:
                file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                
                content = ""
                if file_ext == '.txt':
                    try:
                        content = uploaded_file.read().decode('utf-8')
                    except:
                        try:
                            content = uploaded_file.read().decode('latin-1')
                        except:
                            messages.error(request, "Không thể đọc file txt")
                            return redirect('admin_add_story')
                            
                elif file_ext == '.docx':
                    temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', uploaded_file.name)
                    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                    
                    with open(temp_path, 'wb+') as dest:
                        for chunk in uploaded_file.chunks():
                            dest.write(chunk)
                    
                    try:
                        doc = docx.Document(temp_path)
                        paragraphs = []
                        for para in doc.paragraphs:
                            if para.text.strip():
                                paragraphs.append(para.text)
                        content = '\n'.join(paragraphs)
                        os.remove(temp_path)
                    except Exception as e:
                        messages.error(request, f"Lỗi đọc file docx: {str(e)}")
                        return redirect('admin_add_story')
                
                chapters_data = parse_chapters_from_text(content)
                
                if chapters_data:
                    saved_count = 0
                    for ch_data in chapters_data:
                        if not Chapter.objects.filter(story=story, chapter_number=ch_data['number']).exists():
                            Chapter.objects.create(
                                story=story,
                                chapter_number=ch_data['number'],
                                title=ch_data['title'],
                                content=ch_data['content']
                            )
                            saved_count += 1
                    
                    messages.success(request, f"Đã import {saved_count}/{len(chapters_data)} chương từ file.")
                else:
                    messages.warning(request, "Không tìm thấy chương nào trong file.")
            
            return redirect('admin_dashboard')
        else:
            # In lỗi form ra console để debug
            print(form.errors)
            messages.error(request, "Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.")
    else:
        form = StoryForm()
    
    return render(request, 'admin/add_story.html', {'form': form})

def admin_manage_chapters(request, story_id):
    """Quản lý chương"""
    story = get_object_or_404(Story, id=story_id)
    chapters = story.chapters.all().order_by('chapter_number')
    return render(request, 'admin/manage_chapters.html', {
        'story': story,
        'chapters': chapters
    })

def admin_add_chapter(request, story_id):
    """Thêm chương mới"""
    story = get_object_or_404(Story, id=story_id)
    
    if request.method == 'POST':
        # Lấy dữ liệu từ POST
        chapter_number = request.POST.get('chapter_number')
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        # Kiểm tra dữ liệu
        if chapter_number and title:
            # Kiểm tra xem chương đã tồn tại chưa
            if Chapter.objects.filter(story=story, chapter_number=chapter_number).exists():
                messages.error(request, f"Chương {chapter_number} đã tồn tại!")
            else:
                # Tạo chương mới
                chapter = Chapter.objects.create(
                    story=story,
                    chapter_number=chapter_number,
                    title=title,
                    content=content or ""
                )
                messages.success(request, f"Đã thêm chương {chapter_number}: {title} thành công!")
                return redirect('admin_manage_chapters', story_id=story.id)
        else:
            messages.error(request, "Vui lòng điền đầy đủ thông tin!")
    
    # Lấy số chương tiếp theo
    next_number = story.chapters.count() + 1
    
    return render(request, 'admin/add_chapter.html', {
        'story': story,
        'next_number': next_number
    })

def admin_edit_chapter(request, story_id, chapter_id):
    """Sửa chương"""
    story = get_object_or_404(Story, id=story_id)
    chapter = get_object_or_404(Chapter, id=chapter_id, story=story)
    
    if request.method == 'POST':
        # Lấy dữ liệu từ POST
        chapter_number = request.POST.get('chapter_number')
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        if chapter_number and title:
            # Kiểm tra nếu đổi số chương và số mới đã tồn tại chưa
            if int(chapter_number) != chapter.chapter_number:
                if Chapter.objects.filter(story=story, chapter_number=chapter_number).exists():
                    messages.error(request, f"Chương {chapter_number} đã tồn tại!")
                    return render(request, 'admin/edit_chapter.html', {
                        'story': story,
                        'chapter': chapter
                    })
            
            # Cập nhật chương
            chapter.chapter_number = chapter_number
            chapter.title = title
            chapter.content = content or ""
            chapter.save()
            
            messages.success(request, f"Đã cập nhật chương {chapter_number}: {title} thành công!")
            return redirect('admin_manage_chapters', story_id=story.id)
        else:
            messages.error(request, "Vui lòng điền đầy đủ thông tin!")
    
    return render(request, 'admin/edit_chapter.html', {
        'story': story,
        'chapter': chapter
    })

def admin_delete_story(request, story_id):
    """Xóa truyện"""
    story = get_object_or_404(Story, id=story_id)
    
    if request.method == 'POST':
        story_title = story.title
        chapter_count = story.chapters.count()
        
        if story.cover:
            if os.path.isfile(story.cover.path):
                os.remove(story.cover.path)
        
        story.delete()
        
        messages.success(request, f"✅ Đã xóa truyện '{story_title}' và {chapter_count} chương liên quan!")
        return redirect('admin_dashboard')
    
    return render(request, 'admin/confirm_delete_story.html', {
        'story': story,
        'chapter_count': story.chapters.count()
    })

def admin_delete_chapter(request, story_id, chapter_id):
    """Xóa chương"""
    story = get_object_or_404(Story, id=story_id)
    chapter = get_object_or_404(Chapter, id=chapter_id, story=story)
    
    if request.method == 'POST':
        chapter_number = chapter.chapter_number
        chapter_title = chapter.title
        chapter.delete()
        messages.success(request, f"✅ Đã xóa chương {chapter_number}: {chapter_title}")
        return redirect('admin_manage_chapters', story_id=story.id)
    
    return render(request, 'admin/confirm_delete_chapter.html', {
        'story': story,
        'chapter': chapter
    })

def admin_bulk_delete_chapters(request, story_id):
    """Xóa nhiều chương"""
    story = get_object_or_404(Story, id=story_id)
    
    if request.method == 'POST':
        chapter_ids = request.POST.getlist('chapters')
        if chapter_ids:
            chapters_to_delete = Chapter.objects.filter(id__in=chapter_ids, story=story)
            count = chapters_to_delete.count()
            chapters_to_delete.delete()
            messages.success(request, f"✅ Đã xóa {count} chương!")
        else:
            messages.warning(request, "⚠ Vui lòng chọn ít nhất một chương để xóa!")
        
        return redirect('admin_manage_chapters', story_id=story.id)
    
    return render(request, 'admin/bulk_delete_chapters.html', {
        'story': story,
        'chapters': story.chapters.all()
    })

def parse_chapters_from_text(text):
    """Hàm tách chương từ text"""
    chapters = []
    lines = text.split('\n')
    
    current_chapter = None
    current_content = []
    
    patterns = [
        r'^chương\s+(\d+)[:\s]*(.*)$',
        r'^chapter\s+(\d+)[:\s]*(.*)$',
        r'^chương\s+(\d+)$',
        r'^chapter\s+(\d+)$',
        r'^(\d+)[\.\:\s]+(.*)$',
    ]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        matched = False
        chapter_num = None
        chapter_title = ""
        
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                matched = True
                chapter_num = int(match.group(1))
                if len(match.groups()) > 1:
                    chapter_title = match.group(2).strip()
                break
        
        if matched:
            if current_chapter and current_content:
                current_chapter['content'] = '\n'.join(current_content).strip()
                chapters.append(current_chapter)
            
            current_chapter = {
                'number': chapter_num,
                'title': chapter_title if chapter_title else f"Chương {chapter_num}",
                'content': ""
            }
            current_content = []
        elif current_chapter:
            current_content.append(line)
    
    if current_chapter and current_content:
        current_chapter['content'] = '\n'.join(current_content).strip()
        chapters.append(current_chapter)
    
    if not chapters and text.strip():
        chapters.append({
            'number': 1,
            'title': 'Chương 1',
            'content': text.strip()
        })
    
    return chapters