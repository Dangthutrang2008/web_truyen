from django.db import models
from django.utils import timezone

class Story(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tên truyện")
    author = models.CharField(max_length=100, verbose_name="Tác giả")
    description = models.TextField(verbose_name="Mô tả")
    cover = models.ImageField(upload_to='covers/', blank=True, null=True, verbose_name="Ảnh bìa")
    password = models.CharField(max_length=100, blank=True, null=True, verbose_name="Mật khẩu (để trống nếu mở)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Truyện"
        verbose_name_plural = "Truyện"

    def is_locked(self):
        return bool(self.password)  # True nếu có mật khẩu

    def latest_chapter(self):
        # Lấy chương mới nhất (số chương cao nhất)
        return self.chapters.order_by('-chapter_number').first()

class Chapter(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='chapters', verbose_name="Truyện")
    chapter_number = models.IntegerField(verbose_name="Số chương")
    title = models.CharField(max_length=200, verbose_name="Tên chương")
    content = models.TextField(verbose_name="Nội dung")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.story.title} - Chương {self.chapter_number}: {self.title}"

    class Meta:
        ordering = ['chapter_number']  # Sắp xếp theo số chương tăng dần
        verbose_name = "Chương"
        verbose_name_plural = "Chương"
        unique_together = ('story', 'chapter_number')  # Đảm bảo không trùng số chương