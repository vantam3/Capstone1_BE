from django.db import models

from django.db import models

class Book(models.Model):
    book_id = models.AutoField(primary_key=True)  # Tự động tăng ID cho sách
    title = models.CharField(max_length=255)  # Tiêu đề sách
    author = models.CharField(max_length=255)  # Tác giả
    isbn = models.CharField(max_length=13, unique=True)  # ISBN phải là duy nhất
    description = models.TextField(null=True, blank=True)  # Mô tả sách
    language = models.CharField(max_length=50)  # Ngôn ngữ của sách
    cover_image = models.URLField(max_length=500, null=True, blank=True)  # URL ảnh bìa sách
    total_pages = models.IntegerField(null=True, blank=True)  # Số trang của sách
    view_count = models.IntegerField(default=0)  # Số lượt xem
    status = models.CharField(max_length=50, null=True, blank=True)  # Trạng thái (còn hàng, hết hàng...)
    create_at = models.DateTimeField(auto_now_add=True)  # Ngày tạo
    update_at = models.DateTimeField(auto_now=True)  # Ngày cập nhật

    def __str__(self):
        return self.title

