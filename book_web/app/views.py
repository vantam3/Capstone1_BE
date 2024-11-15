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

# app/views.py
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from rest_framework import generics, status
from .serializers import BookSerializer, ReviewSerializer
from rest_framework.filters import SearchFilter
from .models import Book, Review
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote


def home(request):
    return HttpResponse("Bookquest")

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Đăng ký thành công!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Đăng nhập thành công!')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('login')

class BookSearchAPIView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [SearchFilter]
    search_fields = ['title', 'author']

def all_books(request):
    books = Book.objects.all().values('title', 'author', 'download_link', 'slug', 'image', 'id')
    
    # Kiểm tra và xây dựng URL đầy đủ cho image nếu cần thiết
    books_data = []
    for book in books:
        if book['image']:
            # Nếu image là một đường dẫn tương đối (trường hợp ImageField)
            if not book['image'].startswith('http'):
                book['image'] = request.build_absolute_uri(book['image'])
        books_data.append(book)

    return JsonResponse(books_data, safe=False)

def book_detail_view(request, book_id):
    # Lấy đối tượng từ database
    book = get_object_or_404(Book, id=book_id)

    # Xử lý URL hình ảnh
    image_url = None
    if book.image:
        if hasattr(book.image, 'url'):  # Trường hợp ImageField
            image_url = request.build_absolute_uri(book.image.url)
        else:  # Trường hợp image là một chuỗi
            if book.image.startswith(('http://', 'https://')):
                image_url = book.image  # Sử dụng URL đầy đủ trực tiếp
            else:
                # Nếu là đường dẫn tương đối, thêm MEDIA_URL
                image_url = request.build_absolute_uri(settings.MEDIA_URL + book.image)

                
    print(f"Original image: {book.image}")
    print(f"Processed image_url: {image_url}")


    # Chuẩn bị JSON trả về
    book_data = {
        'title': book.title,
        'author': book.author,
        'download_link': book.download_link,
        'image': image_url,
        'id': book.id,
        'slug': book.slug,
    }
    return JsonResponse(book_data)


def books_by_author(request, author_name):
    books = Book.objects.filter(author__icontains=author_name).values('title', 'author', 'slug', 'download_link')
    return JsonResponse(list(books), safe=False)

def book_content_by_id(request, book_id):
    # Truy xuất sách dựa trên book_id thay vì slug
    book = get_object_or_404(Book, id=book_id)
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

    # Trả về JSON chứa thông tin sách và nội dung
    return JsonResponse({
        'title': book.title,
        'author': book.author,
        'content': content_text,
    })
import json

@login_required  # Yêu cầu người dùng phải đăng nhập để sử dụng endpoint này
@csrf_exempt  # Tạm thời bỏ qua CSRF trong môi trường phát triển
def add_review(request, book_id):
    if request.method == 'POST':
        try:
            # Parse JSON data từ body của yêu cầu
            data = json.loads(request.body)

            book = get_object_or_404(Book, id=book_id)
            rating = data.get('rating')
            comment = data.get('comment', '').strip()

            # Kiểm tra rating hợp lệ
            if rating and 1 <= int(rating) <= 5:
                review = Review.objects.create(
                    book=book,
                    user=request.user,  # Đảm bảo người dùng đã đăng nhập được gán vào Review
                    rating=int(rating),
                    comment=comment
                )
                return JsonResponse({
                    "id": review.id,
                    "user": review.user.username,
                    "rating": review.rating,
                    "comment": review.comment,
                    "created_at": review.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }, status=201)
            else:
                return JsonResponse({"error": "Invalid rating"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=400)

def get_book_reviews(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    reviews = book.reviews.select_related('user').values('user__username', 'rating', 'comment', 'created_at')
    return JsonResponse({
        "title": book.title,
        "reviews": list(reviews)
    })
