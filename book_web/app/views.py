from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status
from .serializers import BookSerializer, ReviewSerializer
from rest_framework.filters import SearchFilter
from .models import Book,Genre
import requests
from bs4 import BeautifulSoup
from rest_framework.decorators import api_view
import random
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


def home(request):
    return HttpResponse("Bookquest")

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        username = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')

        if password != confirm_password:
            return Response({'error': 'Passwords do not match!'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Email already exists!'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            email=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)
    
class LoginView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')

        try:
            # Lookup user by email
            user = User.objects.get(email=email)

            # Authenticate using the user's username
            auth_user = authenticate(request, username=user.username, password=password)

            if auth_user is None:
                return Response({'message': 'Invalid password!'}, 
                                status=status.HTTP_401_UNAUTHORIZED)

            # Generate token
            refresh = RefreshToken.for_user(auth_user)
            return Response({
                'token': str(refresh.access_token),
                'user': {
                    'id': auth_user.id,
                    'first_name': auth_user.first_name,
                    'last_name': auth_user.last_name,
                    'email': auth_user.email
                }
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'message': 'User with this email does not exist!'}, 
                            status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        try:
            # Lấy refresh token từ request
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()  # Thêm token vào danh sách blacklist

            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
    
    
# ------------------- ADMIN VIEWS -------------------     
    
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import permission_classes
import time


@api_view(['GET'])
# @permission_classes([IsAdminUser])
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
# @permission_classes([IsAdminUser])
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
# @permission_classes([IsAdminUser])
def delete_user(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    user.delete()
    return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)

#CRUD BOOKS
#ADD BOOKS
@api_view(['POST'])
# @permission_classes([IsAdminUser])
def fetch_books_by_genre(request):
    keyword = request.data.get('keyword', '').lower()  # Từ khóa admin nhập
    size = min(int(request.data.get('size', 20)), 100)  # Giới hạn số sách
    max_page = 100
    max_attempts = 10  # Giới hạn số lần thử chuyển trang
    found_books = 0

    if not keyword:
        return Response({"error": "Keyword is required"}, status=400)

    added_books = []
    download_links = []
    
    # Tạo hoặc lấy thể loại từ keyword
    genre, _ = Genre.objects.get_or_create(name=keyword.capitalize())

    for attempt in range(max_attempts):
        random_page = random.randint(1, max_page)  # Chọn trang ngẫu nhiên
        url = f"https://gutendex.com/books?languages=en&page={random_page}&size={size}"
        response = requests.get(url)

        if response.status_code != 200:
            continue  # Chuyển sang trang khác nếu API thất bại

        data = response.json()
        books_on_page = 0

        for book_data in data['results']:
            # Tìm kiếm từ khóa trong tiêu đề hoặc mô tả (summary)
            title = book_data['title'].lower()
            subjects = ", ".join(book_data.get('subjects', [])).lower()
            
            if keyword not in title and keyword not in subjects:
                continue

            # Lấy thông tin sách
            author = book_data['authors'][0]['name'] if book_data['authors'] else 'Unknown'
            formats = book_data.get('formats', {})
            download_link = formats.get('text/html') or formats.get('text/plain; charset=utf-8')
            image_link = formats.get('image/jpeg')
            language = book_data.get('languages', ['Unknown'])[0]

            if image_link and download_link:
                # Cập nhật hoặc tạo sách
                book, created = Book.objects.update_or_create(
                    gutenberg_id=book_data['id'],
                    defaults={
                        'title': book_data['title'],
                        'author': author,
                        'download_link': download_link,
                        'image': image_link,
                        'summary': subjects,
                        'language': language,
                    }
                )

                # Gắn thể loại vào sách
                book.genres.add(genre)

                if created:
                    added_books.append({
                        "title": book.title,
                        "author": book.author,
                        "image": book.image,
                        "summary": book.summary,
                        "language": book.language,
                    })
                    download_links.append(download_link)
                    books_on_page += 1
                    found_books += 1

            if found_books >= size:
                break  # Đủ số lượng sách yêu cầu

        if found_books >= size or books_on_page > 0:
            break  # Kết thúc nếu tìm thấy sách trên trang này

    if found_books == 0:
        return Response({"error": f"No books found matching keyword '{keyword}' after {max_attempts} attempts."}, status=404)

    # Tạo file txt và lưu các link download
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"downloads_{timestamp}.txt"
    file_path = os.path.join("app/data", file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        for link in download_links[:size]:  # Ghi đúng số lượng sách được yêu cầu
            file.write(link + "\n")

    return Response({
        "message": f"Successfully fetched {len(added_books)} books matching keyword '{keyword}'",
        "books": added_books,
        "download_file": file_name,  # Trả về tên file
    }, status=200)




