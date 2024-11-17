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
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
import random
import os
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from datetime import datetime



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

@api_view(['GET'])
def all_books(request):
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def book_detail_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    serializer = BookSerializer(book)
    return Response(serializer.data)


@api_view(['GET'])
def books_by_author(request, author_name):
    books = Book.objects.filter(author__icontains=author_name)
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def book_content_by_id(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    content_text = "No content available"

    if book.download_link:
        try:
            response = requests.get(book.download_link)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')

                if 'text/html' in content_type:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for img_tag in soup.find_all('img'):
                        img_src = img_tag.get('src')
                        if img_src and img_src.startswith('//'):
                            img_tag['src'] = 'https:' + img_src

                    content_text = str(soup)
                else:
                    content_text = f"<pre>{response.text}</pre>"
            else:
                content_text = f"Failed to fetch content, status code: {response.status_code}"
        except Exception as e:
            content_text = f"Error fetching content: {e}"

    return Response({
        'title': book.title,
        'author': book.author,
        'content': content_text,
    })


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def add_review(request, book_id):
    # Lấy sách
    book = get_object_or_404(Book, id=book_id)

    # Kiểm tra người dùng đã đăng nhập
    if not request.user.is_authenticated:
        return Response({"error": "User must be authenticated"}, status=403)

    # Lấy dữ liệu từ request
    data = request.data
    data['book'] = book.id  # Gán ID của sách vào dữ liệu

    # Tạo serializer với dữ liệu và request context
    serializer = ReviewSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user, book=book)  # Gán user và book
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def get_book_reviews(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    reviews = book.reviews.all()
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)
    
    # admin
     
    
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import permission_classes

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_users(request):
    users = User.objects.all()
    data = [{'id': user.id, 'username': user.username, 'email': user.email, 'is_staff': user.is_staff} for user in users]
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_books(request):
    books = Book.objects.all()
    data = [{'id': book.id, 'title': book.title, 'author': book.author, 'download_link': book.download_link} for book in books]
    return Response(data)

#CRUD USERS
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_user(request):
    data = request.data
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=data['username']).exists():
        return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )
    return Response({"id": user.id, "username": user.username, "email": user.email}, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_user(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    if 'password' in data:
        user.set_password(data['password'])
    user.save()

    return Response({"id": user.id, "username": user.username, "email": user.email}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_user(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    user.delete()
    return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)

#CRUD BOOKS
#ADD BOOKS
@api_view(['POST'])
# @permission_classes([IsAdminUser])  # Chỉ admin mới có quyền
def fetch_and_add_books(request):
    size = min(int(request.data.get('size', 20)), 100)  # Giới hạn tối đa là 100
    max_page = 100  # Số trang tối đa (cố định)
    random_page = random.randint(1, max_page)  # Chọn trang ngẫu nhiên

    url = f"https://gutendex.com/books?languages=en&page={random_page}&size={size}"
    response = requests.get(url)

    if response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch data from API"}, status=500)

    data = response.json()
    added_books = []
    download_links = []

    for book_data in data['results']:
        title = book_data['title']
        author = book_data['authors'][0]['name'] if book_data['authors'] else 'Unknown'
        formats = book_data.get('formats', {})

        # Các trường bổ sung
        summary = ", ".join(book_data.get('Summary', []))  # Sử dụng subjects làm summary nếu có
        credits = ", ".join([credit['name'] for credit in book_data.get('Credits', [])])  # Lấy danh sách translators
        language = book_data.get('languages', ['Unknown'])[0]  # Ngôn ngữ
        note = ", ".join(book_data.get('Note', []))  # Bookshelves có thể làm ghi chú

        # Link ảnh và link download
        image_link = formats.get('image/jpeg')
        download_link = (
            formats.get('text/html') or
            formats.get('text/plain; charset=utf-8') or
            formats.get('text/plain') or
            formats.get('text/html.images')
        )

        # Kiểm tra nếu có link ảnh và link download hợp lệ
        if image_link and download_link:
            # Dùng `update_or_create` để lưu vào cơ sở dữ liệu
            book, created = Book.objects.update_or_create(
                gutenberg_id=book_data['id'],
                defaults={
                    'title': title,
                    'author': author,
                    'download_link': download_link,
                    'image': image_link,
                    'summary': summary or None,  # Nếu không có thì lưu None
                    'credits': credits or None,
                    'language': language or None,
                    'note': note or None,
                }
            )
            if created:
                added_books.append({
                    "title": book.title,
                    "author": book.author,
                    "image": book.image,
                    "summary": book.summary,
                    "credits": book.credits,
                    "language": book.language,
                    "note": book.note,
                    "download_link": book.download_link,
                })
                # Thêm link download vào danh sách
                download_links.append(download_link)

    # Tạo file txt và lưu các link download
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # Tạo timestamp cho file
    file_name = f"downloads_{timestamp}.txt"
    file_path = os.path.join("app/data", file_name)  # Thư mục lưu file

    # Tạo thư mục nếu chưa tồn tại
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Ghi các link download vào file
    with open(file_path, "w", encoding="utf-8") as file:
        for link in download_links:
            file.write(link + "\n")

    return JsonResponse({
        "message": f"Successfully fetched {len(added_books)} books from random page {random_page}",
        "books": added_books,
        "download_file": file_name  # Trả về tên file để tham khảo
    }, status=200)
