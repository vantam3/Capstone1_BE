from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status, permissions
from .serializers import BookSerializer, ReviewSerializer,FavoriteBook,FavoriteBookSerializer,ReadingHistorySerializer, ResetPasswordSerializer
from rest_framework.filters import SearchFilter
from .models import Book, Genre, UserBook
import requests
from bs4 import BeautifulSoup
from rest_framework.decorators import api_view
import random
import os
import string
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Avg
from django.core.mail import send_mail
from django.core.cache import cache
from .serializers import UserBookSerializer
from django.db.models import Max


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

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist!'}, status=status.HTTP_404_NOT_FOUND)

        # Generate a confirmation code
        confirmation_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

        # Store the confirmation code in cache with a timeout (e.g., 10 minutes)
        cache.set(f"password_reset_code_{email}", confirmation_code, timeout=600)

        try:
            send_mail(
                subject="Confirmation Code - Bookquest",
                message=f"Hello {user.first_name},\n\nYour confirmation code is: {confirmation_code}\nUse this code to reset your password.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            return Response({'message': 'Confirmation code sent to your email!'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Failed to send email. Please try again later.', 'details': str(e)}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        confirmation_code = serializer.validated_data['confirmation_code']
        new_password = serializer.validated_data['new_password']

        # Retrieve the confirmation code from cache
        cached_code = cache.get(f"password_reset_code_{email}")

        if not cached_code or cached_code != confirmation_code:
            return Response({'error': 'Invalid or expired confirmation code!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist!'}, status=status.HTTP_404_NOT_FOUND)

        # Update the password
        user.set_password(new_password)
        user.save()

        # Clear the confirmation code from cache
        cache.delete(f"password_reset_code_{email}")

        return Response({'message': 'Password has been reset successfully!'}, status=status.HTTP_200_OK)
            
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
    
    # Tính toán trung bình rating từ các review của sách
    average_rating = book.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Serialize dữ liệu của sách
    serializer = BookSerializer(book)
    
    # Cập nhật thêm trường average_rating vào dữ liệu trả về
    book_data = serializer.data
    book_data['average_rating'] = round(average_rating, 1)  # Làm tròn trung bình rating
    
    return Response(book_data)

class CreateUserBookView(APIView):
    # Require the user to be authenticated
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Extract data from the request
        title = request.data.get('title')
        genre = request.data.get('genre')
        description = request.data.get('description')
        content = request.data.get('text')  
        cover_image = request.FILES.get('cover_image')  # Get the uploaded file if present
        
        # Get the authenticated user from the request
        user = request.user

        # Combine first_name and last_name for the author field
        author_name = f"{user.first_name} {user.last_name}".strip()

        # Validate required fields
        if not title or not genre or not description or not content:
            return Response({'error': 'All fields are required except cover image.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new UserBook entry with is_approved explicitly set to False
        try:
            user_book = UserBook.objects.create(
                title=title,
                author=author_name,
                genre=genre,
                description=description,
                content=content,
                cover_image=cover_image,
                user=user,
                is_approved=False 
            )
            return Response({
                'message': 'Book created successfully and awaits admin approval!',
                'book_id': user_book.id
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListUserBooksView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request):
        # Fetch all books that are not approved
        books = UserBook.objects.filter(is_approved=False)
        serializer = UserBookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ListApprovedBooksView(APIView):
    """
    API to list all approved books (is_approved=True).
    """
    def get(self, request):
        # Lấy tất cả các sách đã được duyệt
        approved_books = UserBook.objects.filter(is_approved=True)
        serializer = UserBookSerializer(approved_books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
################################################
import re

def is_valid_url(string):
    """
    Kiểm tra xem chuỗi có phải là URL hợp lệ hay không.
    """
    regex = re.compile(
        r'^(http|https)://'  # Chỉ chấp nhận http:// hoặc https://
        r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}'  # Tên miền
        r'(:[0-9]{1,5})?'  # Tùy chọn cổng
        r'(/.*)?$',  # Đường dẫn tùy chọn
        re.IGNORECASE,
    )
    return re.match(regex, string) is not None
from django.db.models import Min

def generate_unique_negative_gutenberg_id():
    """
    Tạo giá trị âm duy nhất cho gutenberg_id.
    """
    # Lấy giá trị nhỏ nhất của gutenberg_id hiện tại
    min_id = Book.objects.aggregate(Min('gutenberg_id'))['gutenberg_id__min']
    if min_id is None or min_id >= 0:  # Nếu không có ID âm hoặc không có sách nào
        return -1  # Bắt đầu với -1
    return min_id - 1  # Giảm thêm 1 để tạo ID mới


from datetime import datetime

def map_userbook_to_book(user_book):
    """
    Ánh xạ dữ liệu từ UserBook sang Book.
    """
    download_link = user_book.content

    # Xử lý `download_link` (nếu là URL, giữ nguyên; nếu là nội dung sách, định dạng lại)
    if is_valid_url(download_link):
        formatted_link = download_link
    else:
        formatted_link = f"Content: {download_link}"  # Đánh dấu nội dung là text

    return {
        "title": user_book.title,
        "author": user_book.author,
        "download_link": formatted_link,
        "image": user_book.cover_image or "/default-cover.jpg",
        "subject": user_book.description or "No description available",
        "create_at": datetime.now(),
    }
from django.db.models import Max
from datetime import datetime
from app.models import Book, UserBook, Genre

def get_community_creations_genre():
    """
    Lấy hoặc tạo thể loại 'Community Creations' trong bảng Genre.
    """
    genre, _ = Genre.objects.get_or_create(name="Community Creations")
    return genre

def approve_user_book(user_book_id):
    """
    Phê duyệt sách từ UserBook và thêm vào app_book với gutenberg_id âm.
    """
    try:
        user_book = UserBook.objects.get(id=user_book_id)

        if not user_book.is_approved:
            user_book.is_approved = True
            user_book.save()

        # Gán gutenberg_id âm duy nhất
        gutenberg_id = generate_unique_negative_gutenberg_id()

        # Tạo sách mới trong app_book
        book = Book.objects.create(
            title=user_book.title,
            author=user_book.author,
            gutenberg_id=generate_unique_negative_gutenberg_id(),  # Gọi hàm tạo ID âm
            download_link=user_book.content,
            image=user_book.cover_image or "/default-cover.jpg",
            subject=user_book.description or "No description available",
            create_at=datetime.now(),
        )

        # Gắn thể loại "Community Creations"
        community_genre, _ = Genre.objects.get_or_create(name="Community Creations")
        book.genres.add(community_genre)

        return {"status": "success", "message": "Book approved and added to Community Creations."}
    except UserBook.DoesNotExist:
        return {"status": "error", "message": "User book not found."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


##########
# API to approve a specific user-submitted book
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

class ApproveUserBookView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def put(self, request, user_book_id):
        result = approve_user_book(user_book_id)  # Gọi hàm xử lý
        if result["status"] == "success":
            return Response({"message": result["message"]}, status=status.HTTP_200_OK)
        return Response({"message": result["message"]}, status=status.HTTP_400_BAD_REQUEST)






#########################################
@api_view(['GET'])
def books_by_author(request, author_name):
    books = Book.objects.filter(author__icontains=author_name)
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def book_content_by_id(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Kiểm tra nếu linkdownload là URL
    if book.download_link.startswith("http://") or book.download_link.startswith("https://"):
        try:
            response = requests.get(book.download_link)
            if response.status_code == 200:
                content_text = response.text  # Nội dung từ URL
            else:
                content_text = "No content available"  # Nội dung mặc định nếu không tải được
        except Exception:
            content_text = "No content available"  # Nội dung mặc định khi có lỗi
    else:
        # Nếu không phải URL, sử dụng trực tiếp nội dung từ linkdownload
        content_text = book.download_link or "No content available"

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
    
    
#edit profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Chỉ cho phép người dùng đã xác thực truy cập
def get_user_profile(request, user_id):
    # In ra ID của người dùng đăng nhập (để debug)
    print(f"Logged in user ID: {request.user.id}")

    # Kiểm tra xem user_id trong URL có giống với user ID của người dùng đang đăng nhập không
    if request.user.id != int(user_id):  # Chuyển user_id sang kiểu int
        return Response({"error": "You can only view your own profile."}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(pk=user_id)  # Lấy người dùng từ DB bằng user_id
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Trả về thông tin người dùng
    response_data = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.email = data.get('email', user.email)
    
    # Cập nhật mật khẩu nếu có
    if 'password' in data:
        user.set_password(data['password'])

    user.save()

    return Response({
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email
    }, status=status.HTTP_200_OK)

#change password
from rest_framework import views  # Import views từ rest_framework
from .serializers import ChangePasswordSerializer  # Import serializer từ file serializers.py
class ChangePasswordView(views.APIView):
    permission_classes = [IsAuthenticated]  # Chỉ người dùng đã đăng nhập mới có thể thay đổi mật khẩu
    
    def put(self, request):
        user = request.user  # Lấy thông tin người dùng từ request (yêu cầu phải đăng nhập)
        data = request.data
        serializer = ChangePasswordSerializer(data=data)
        
        if serializer.is_valid():
            old_password = serializer.validated_data["old_password"]
            new_password = serializer.validated_data["new_password"]
            confirm_password = serializer.validated_data["confirm_password"]

            # Kiểm tra mật khẩu cũ có đúng không
            if not user.check_password(old_password):
                return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

            # Kiểm tra mật khẩu mới và xác nhận mật khẩu có khớp không
            if new_password != confirm_password:
                return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

            # Cập nhật mật khẩu mới
            user.set_password(new_password)
            user.save()
            
            return Response({"success": "Password changed successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
################################################################################
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import FavoriteBook, Book
from django.contrib.auth.models import User

@api_view(['POST'])
def add_to_favorites(request):
    # Xác nhận người dùng đã đăng nhập
    if not request.user.is_authenticated:
        return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    book_id = request.data.get('book_id')
    if not book_id:
        return Response({"error": "Book ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        book = Book.objects.get(id=book_id)
        user = request.user

        # Kiểm tra nếu sách đã được yêu thích bởi người dùng
        if FavoriteBook.objects.filter(user=user, book=book).exists():
            return Response({"message": "Book already added to favorites!"}, status=status.HTTP_200_OK)

        # Thêm sách vào danh sách yêu thích của người dùng
        FavoriteBook.objects.create(user=user, book=book)
        return Response({"message": "Book added to favorites!"}, status=status.HTTP_200_OK)

    except Book.DoesNotExist:
        return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
    
    
#history user
from .models import Book, ReadingHistory
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_reading_history(request):
    book_id = request.data.get('book_id')
    if not book_id:
        return Response({"error": "Book ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        book = Book.objects.get(id=book_id)
        ReadingHistory.objects.create(user=request.user, book=book)
        return Response({"message": "Book added to reading history"}, status=status.HTTP_201_CREATED)
    except Book.DoesNotExist:
        return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
   
   
 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reading_history(request):
    """
    API để lấy lịch sử đọc của người dùng hiện tại.
    """
    user = request.user
    history = ReadingHistory.objects.filter(user=user).order_by('-read_at')  # Lịch sử gần nhất trước
    serializer = ReadingHistorySerializer(history, many=True)
    return Response(serializer.data)

# Trong views.py
@api_view(['GET'])
def get_favorites(request):
    if not request.user.is_authenticated:
        return Response({"error": "User is not authenticated"}, status=401)

    # Lấy danh sách sách yêu thích của người dùng
    favorite_books = FavoriteBook.objects.filter(user=request.user)
    books = [favorite_book.book for favorite_book in favorite_books]

    # Chuyển dữ liệu thành định dạng JSON
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def remove_from_favorites(request):
    if not request.user.is_authenticated:
        return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    book_id = request.data.get('book_id')
    
    if not book_id:
        return Response({"error": "Book ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Tìm sách bằng book_id
        book = Book.objects.get(id=book_id)

        # Tìm đối tượng FavoriteBook để xóa
        user = request.user
        favorite = FavoriteBook.objects.filter(user=user, book=book).first()

        if favorite:
            favorite.delete()  # Xóa khỏi danh sách yêu thích
            return Response({"message": "Book removed from favorites!"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Book is not in favorites."}, status=status.HTTP_400_BAD_REQUEST)
    
    except Book.DoesNotExist:
        return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
def rating_statistics(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT rating, COUNT(*) AS count
            FROM book_web.app_review
            GROUP BY rating
            ORDER BY rating
        """)
        rating_data = cursor.fetchall()
    rates = {row[0]: row[1] for row in rating_data}
    total_rates = sum(rates.values())
    weighted_sum = sum(rating * count for rating, count in rates.items())
    average_rating = round(weighted_sum / total_rates, 2) if total_rates > 0 else 0

    return Response({
        "rates": rates,
        "average_rating": average_rating,
    })

@api_view(['GET'])
def report_statistics(request):
    # Tổng số sách
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM app_book;")
        total_books = cursor.fetchone()[0]

    # Tổng lượt đọc và sách được đọc nhiều nhất
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT book_id, COUNT(*) AS read_count
            FROM app_readinghistory
            GROUP BY book_id
            ORDER BY read_count DESC
            LIMIT 1;
        """)
        most_read_book = cursor.fetchone()
        total_reads = 0
        most_read_book_id = None
        most_read_book_count = 0
        if most_read_book:
            most_read_book_id, most_read_book_count = most_read_book
        
        # Tổng số lượt đọc
        cursor.execute("SELECT COUNT(*) FROM app_readinghistory;")
        total_reads = cursor.fetchone()[0]

    # Tổng số người dùng
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM auth_user;")
        total_users = cursor.fetchone()[0]

    # Tổng số lượt đánh giá và đánh giá trung bình
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*), AVG(rating)
            FROM app_review;
        """)
        review_stats = cursor.fetchone()
        total_reviews = review_stats[0]
        average_rating = review_stats[1] if review_stats[1] is not None else 0

    # Lấy thông tin chi tiết sách được đọc nhiều nhất
    most_read_book_details = None
    if most_read_book_id:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, title, author
                FROM app_book
                WHERE id = %s;
            """, [most_read_book_id])
            most_read_book_details = cursor.fetchone()
            if most_read_book_details:
                most_read_book_details = {
                    "id": most_read_book_details[0],
                    "title": most_read_book_details[1],
                    "author": most_read_book_details[2],
                    "read_count": most_read_book_count,
                }

    return Response({
        "total_books": total_books,
        "total_reads": total_reads,
        "most_read_book": most_read_book_details,
        "total_users": total_users,
        "total_reviews": total_reviews,
        "average_rating": round(average_rating, 2),
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

