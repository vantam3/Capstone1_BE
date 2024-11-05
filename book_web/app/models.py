from django.db import models
from django.contrib.auth.models import User

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

class Review(models.Model):
    book = models.ForeignKey(Book, related_name="reviews", on_delete=models.CASCADE)  # Liên kết đến sách
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Người dùng đánh giá
    rating = models.PositiveSmallIntegerField()  # Xếp hạng (từ 1 đến 5)
    content = models.TextField(null=True, blank=True)  # Nội dung đánh giá
    created_at = models.DateTimeField(auto_now_add=True)  # Ngày tạo đánh giá

    def __str__(self):
        return f"{self.user.username} - {self.book.title} - {self.rating}"

