# myapp/models.py

from django.db import models
from django.utils.text import slugify

class Book(models.Model):
    title = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    author = models.CharField(max_length=255, null=True, blank=True)
    download_link = models.URLField()
    gutenberg_id = models.IntegerField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Book.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(null=True, blank=True)  # Điểm đánh giá từ 1 đến 5
    comment = models.TextField(null=True, blank=True)  # Nội dung bình luận
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.book.title} - Rating: {self.rating}"
