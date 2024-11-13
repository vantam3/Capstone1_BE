import requests
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status
from .serializers import BookSerializer
from rest_framework.filters import SearchFilter
from .models import Book,Review
from django.shortcuts import get_object_or_404
from bs4 import BeautifulSoup
from django.views.decorators.csrf import csrf_exempt  
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from .serializers import RegisterSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny

def home(request):
    return HttpResponse("Bookquest")
#api register
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

User = get_user_model()

# API login
@api_view(['POST'])
def login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        # Get the user with the given email
        user = User.objects.get(email=email)
        # Verify the password
        if check_password(password, user.password):
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "username": user.username}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Incorrect email or password"}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({"error": "Incorrect email or password"}, status=status.HTTP_401_UNAUTHORIZED)

# Protected view
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": "This is secure data. You have successfully logged in!"})


class BookSearchAPIView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [SearchFilter]
    search_fields = ['title', 'author']

def all_books(request):
    books = Book.objects.all().values('title', 'author', 'download_link', 'slug')
    return JsonResponse(list(books), safe=False)
def books_by_author(request, author_name):
    books = Book.objects.filter(author__icontains=author_name).values('title', 'author', 'slug', 'download_link')
    return JsonResponse(list(books), safe=False)

from bs4 import BeautifulSoup
import requests
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from app.models import Book

def book_content_by_slug(request, slug):
    book = get_object_or_404(Book, slug=slug)
    content_text = "No content available"

    if book.download_link:
        try:
            response = requests.get(book.download_link)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')

                # Kiểm tra nếu nội dung là HTML
                if 'text/html' in content_type:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Xử lý thẻ <img> để đảm bảo đường dẫn đầy đủ cho các hình ảnh
                    for img_tag in soup.find_all('img'):
                        img_src = img_tag.get('src')
                        if img_src and img_src.startswith('//'):
                            img_tag['src'] = 'https:' + img_src

                    content_text = str(soup)  # Nội dung HTML đầy đủ

                # Nếu không phải HTML, sử dụng văn bản thuần
                else:
                    content_text = f"<pre>{response.text}</pre>"
            else:
                content_text = f"Failed to fetch content, status code: {response.status_code}"
        except Exception as e:
            content_text = f"Error fetching content: {e}"

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