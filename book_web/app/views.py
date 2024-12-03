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
    
    # admin
     
    
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
@permission_classes([IsAdminUser])  # Chỉ admin mới có quyền
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
    
    
    
#add book for gernes
@api_view(['POST'])
# @permission_classes([IsAdminUser])  # Chỉ admin mới có quyền sử dụng API
def fetch_books_by_category(request):
    genre_name = request.data.get('genre')  # Lấy thể loại từ admin nhập
    size = min(int(request.data.get('size', 20)), 100)  # Số lượng sách cần lấy
    max_page = 100
    random_page = random.randint(1, max_page)

    if not genre_name:
        return Response({"error": "Genre is required"}, status=400)

    # Tìm kiếm sách trên Gutenberg theo thể loại
    url = f"https://gutendex.com/books?languages=en&page={random_page}&size={size}&search={genre_name}"
    response = requests.get(url)

    if response.status_code != 200:
        return Response({"error": "Failed to fetch data from API"}, status=500)

    data = response.json()
    added_books = []

    for book_data in data['results']:
        title = book_data['title']
        author = book_data['authors'][0]['name'] if book_data['authors'] else 'Unknown'
        formats = book_data.get('formats', {})
        download_link = formats.get('text/html') or formats.get('text/plain; charset=utf-8')
        image_link = formats.get('image/jpeg')

        # Thông tin bổ sung
        summary = ", ".join(book_data.get('subjects', []))  # Sử dụng subjects làm summary
        language = book_data.get('languages', ['Unknown'])[0]

        # Tạo sách mới hoặc cập nhật nếu đã tồn tại
        book, created = Book.objects.update_or_create(
            gutenberg_id=book_data['id'],
            defaults={
                'title': title,
                'author': author,
                'download_link': download_link,
                'image': image_link,
                'summary': summary,
                'language': language,
            }
        )

        # Gắn thể loại admin nhập vào sách
        genre, _ = Genre.objects.get_or_create(name=genre_name)
        book.genres.add(genre)

        if created:
            added_books.append({
                "title": book.title,
                "author": book.author,
                "genres": [genre.name],
                "image": book.image,
                "summary": book.summary,
                "language": book.language,
            })

    return Response({
        "message": f"Successfully fetched {len(added_books)} books with genre {genre_name}",
        "books": added_books,
    }, status=200)