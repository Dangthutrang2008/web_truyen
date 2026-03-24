from django.contrib import admin
from .models import Story, Chapter

class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'story', 'chapter_number', 'title', 'created_at', 'content_preview')
    list_filter = ('story', 'created_at')
    search_fields = ('title', 'content')
    list_per_page = 20  # Số lượng hiển thị mỗi trang
    
    def content_preview(self, obj):
        """Hiển thị preview nội dung"""
        if obj.content:
            # Lấy 100 ký tự đầu tiên của nội dung
            preview = obj.content[:100]
            if len(obj.content) > 100:
                preview += '...'
            return preview
        return '<span style="color: red;">⚠️ Chưa có nội dung</span>'
    
    content_preview.short_description = 'Nội dung (Preview)'
    content_preview.allow_tags = True  # Cho phép HTML

class StoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'is_locked', 'chapter_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'author')
    
    def chapter_count(self, obj):
        return obj.chapters.count()
    
    chapter_count.short_description = 'Số chương'
    
    def is_locked(self, obj):
        return '🔒 Khóa' if obj.password else '🔓 Mở'
    
    is_locked.short_description = 'Trạng thái'

# Đăng ký models với admin
admin.site.register(Story, StoryAdmin)
admin.site.register(Chapter, ChapterAdmin)