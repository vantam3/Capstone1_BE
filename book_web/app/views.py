# myapp/views.py
import requests
from django.http import JsonResponse
from .models import Book,Review
from django.shortcuts import get_object_or_404
from bs4 import BeautifulSoup
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  # Import csrf_exempt
from django.contrib.auth.decorators import login_required


def all_books(request):
    books = Book.objects.all().values('title', 'author', 'download_link', 'slug')
    return JsonResponse(list(books), safe=False)
def books_by_author(request, author_name):
    books = Book.objects.filter(author__icontains=author_name).values('title', 'author', 'slug', 'download_link')
    return JsonResponse(list(books), safe=False)

def book_content_by_slug(request, slug):
    # Lấy sách từ database dựa vào slug
    book = get_object_or_404(Book, slug=slug)
    
    # Kiểm tra nếu `download_link` tồn tại
    content_text = "No content available"
    if book.download_link:
        try:
            response = requests.get(book.download_link)
            if response.status_code == 200:
                content_html = response.text
                # Chuyển đổi nội dung HTML sang plain text bằng BeautifulSoup
                soup = BeautifulSoup(content_html, "html.parser")
                content_text = soup.get_text()
            else:
                content_text = f"Failed to fetch content, status code: {response.status_code}"
        except Exception as e:
            content_text = f"Error fetching content: {e}"

    # Trả về nội dung sách dưới dạng JSON
    return JsonResponse({
        'title': book.title,
        'author': book.author,
        'content': content_text,
    })
    
@csrf_exempt
# @login_required  # Yêu cầu người dùng phải đăng nhập
def add_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    rating_value = request.POST.get('rating')
    comment = request.POST.get('comment', '').strip()

    if rating_value:
        rating_value = int(rating_value)
        if rating_value < 1 or rating_value > 5:
            return JsonResponse({"error": "Rating must be between 1 and 5"}, status=400)

    # Tạo review với cả rating và content (nếu có)
    review = Review.objects.create(
        book=book,
        # user=request.user,  # Gán người dùng hiện tại cho review
        rating=rating_value if rating_value else None,
        comment=comment if comment else None
    )
    
    return JsonResponse({
        "message": "Review added successfully",
        # "user": review.user.username,  # Hiển thị tên người dùng
        "rating": review.rating,
        "comment": review.comment
    }, status=201)
def get_book_reviews(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    # reviews = book.reviews.select_related('user').values('user__username', 'rating', 'content', 'created_at')
    reviews = book.reviews.values('rating', 'comment', 'created_at')
    return JsonResponse({
        "title": book.title,
        "reviews": list(reviews)
    })