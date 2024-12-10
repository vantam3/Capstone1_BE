from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status
from .serializers import BookSerializer, ReviewSerializer
from rest_framework.filters import SearchFilter
from .models import Book, Genre
import requests
from bs4 import BeautifulSoup
from rest_framework.decorators import api_view
import random
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
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
                    'email': auth_user.email,
                    'is_superuser': auth_user.is_superuser,
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


def is_admin(user):
    return user.is_authenticated and user.is_superuser  

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def admin_dashboard(request):
    if is_admin(request.user):
        return Response({'message': 'Welcome Admin!'}, status=status.HTTP_200_OK)
    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def search_books(request):
    # Lấy từ khóa tìm kiếm từ query parameters
    query = request.query_params.get('q', '').strip()
    if not query:
        return Response({'error': 'Query parameter "q" is required.'}, status=400)

    # Tìm kiếm sách theo tiêu đề hoặc tác giả
    books = Book.objects.filter(
        Q(title__icontains=query) | Q(author__icontains=query)
    )

    if not books.exists():
        return Response({'message': 'No books found matching your query.'}, status=404)

    # Serialize kết quả
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data, status=200)

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
    
    
# tim so thich nguoi dung

    
# ------------------- ADMIN VIEWS -------------------     
    
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import permission_classes
from django.db.models import Count, Q
from django.db import connection

@api_view(['GET'])
def book_statistics(request):
    # Sử dụng truy vấn SQL thô để đếm số sách theo thể loại từ app_book_genres
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT g.name, COUNT(bg.book_id) AS book_count
            FROM app_book_genres bg
            INNER JOIN app_genre g ON bg.genre_id = g.id
            GROUP BY g.name
            ORDER BY book_count DESC
        """)
        genres_data = cursor.fetchall()

    # Chuyển đổi dữ liệu thành danh sách từ điển
    genres_result = [{"name": row[0], "book_count": row[1]} for row in genres_data]

    # Tổng số sách
    total_books = sum([row[1] for row in genres_data])

    return Response({
        "total_books": total_books,
        "books_by_genre": genres_result,
    })

@api_view(['GET'])
def user_roles_statistics(request):
    # Đếm số lượng người dùng theo vai trò
    roles_data = {
        "Superusers": User.objects.filter(is_superuser=True).count(),
        "Staff": User.objects.filter(is_staff=True, is_superuser=True).count(),
        "Regular Users": User.objects.filter(is_superuser=False, is_staff=False).count(),
    }

    # Đếm số lượng người dùng đang hoạt động
    active_users = User.objects.filter(is_active=True).count()

    return Response({
        "roles": roles_data,
        "active_users": active_users,
        "total_users": User.objects.count()
    })

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


@api_view(['PUT'])
# @permission_classes([IsAdminUser])
def edit_book_fields(request, pk):
    """
    PUT: Chỉ chỉnh sửa các trường title, author, language, và subject của sách.
    """
    try:
        # Lấy sách theo ID
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

    # Lọc dữ liệu cần chỉnh sửa
    valid_fields = ['title', 'author', 'language', 'subject']
    fields_to_update = {key: value for key, value in request.data.items() if key in valid_fields}

    if not fields_to_update:
        return Response(
            {"error": "No valid fields to update."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Cập nhật từng trường
    for field, value in fields_to_update.items():
        setattr(book, field, value)

    # Lưu thay đổi vào cơ sở dữ liệu
    try:
        book.save()
    except Exception as e:
        return Response(
            {"error": f"Failed to update book: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Trả về thông tin sách sau khi cập nhật
    serializer = BookSerializer(book)
    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(['DELETE'])
# @permission_classes([IsAdminUser])
def delete_book(request, book_id):
    """
    API để xóa sách theo ID.
    """
    try:
        # Lấy sách theo ID
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response(
            {"error": "Book not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        # Xóa sách
        book.delete()
        return Response(
            {"message": "Book deleted successfully"},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        # Xử lý các lỗi không mong muốn
        return Response(
            {"error": f"Failed to delete book: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

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
            # Tìm kiếm từ khóa trong tiêu đề hoặc mô tả (subject)
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
                        'subject': subjects,
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
                        "subject": book.subject,
                        "language": book.language,
                    })
                    books_on_page += 1
                    found_books += 1

            if found_books >= size:
                break  # Đủ số lượng sách yêu cầu

        if found_books >= size or books_on_page > 0:
            break  # Kết thúc nếu tìm thấy sách trên trang này

    if found_books == 0:
        return Response({"error": f"No books found matching keyword '{keyword}' after {max_attempts} attempts."}, status=404)

    return Response({
        "message": f"Successfully fetched {len(added_books)} books matching keyword '{keyword}'",
        "books": added_books,
    }, status=200)

