# app/urls.py
from .views import RegisterView, LoginView, LogoutView
from django.urls import path
from . import views
from .views import search_books
from .views import list_users, list_books
from .views import create_user, update_user, delete_user, fetch_and_add_books,fetch_books_by_category
from .views import admin_dashboard, book_statistics, user_roles_statistics
from .views import ForgotPasswordView, BookCreationAPIView

urlpatterns = [
    path('', views.home, name='home'),
    #Đăng ký
    path('api/register/', RegisterView.as_view(), name='register'),
    #Đăng nhập
    path('api/login/', LoginView.as_view(), name='login'),
    #Đăng xuất
    path('api/logout/', LogoutView.as_view(), name='logout'),
    #Quên Mật khẩu
    path('api/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    #Tìm sách
    path('api/search-books/', search_books, name='search-books'), 
    #Tạo sách
    path('api/create-book/', BookCreationAPIView.as_view(), name='create-book'),
    #Trang Admin:
    path('api/admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('api/book-statistics/', book_statistics, name='book-statistics'),
    path('api/user-roles-statistics/', user_roles_statistics, name='user-roles-statistics'),
    #xem sach
    path('api/books/', views.all_books, name='all_books'),
    path('api/books/<int:book_id>/', views.book_detail_view, name='book_detail_view'),

    path('api/books/<int:book_id>/content/', views.book_content_by_id, name='book_content_by_id'),
    path('api/books/author/<str:author_name>/', views.books_by_author, name='books_by_author'),

    # API endpoints for reviews
    path('api/books/<int:book_id>/add_review/', views.add_review, name='add_review'),
    path('api/books/<int:book_id>/reviews/', views.get_book_reviews, name='get_book_reviews'),
    
    
    #admin
    path('api/admin/users/', list_users, name='list_users'),
    path('api/admin/books/', list_books, name='list_books'),
    
    path('api/admin/users/create/', create_user, name='create_user'),
    path('api/admin/users/<int:user_id>/update/', update_user, name='update_user'),
    path('api/admin/users/<int:user_id>/delete/', delete_user, name='delete_user'),
    
    #add sach
    path('api/admin/fetch-books/', fetch_and_add_books, name='fetch_books'),
    #add book for gernes
    path('api/admin/fetch-books-gernes/', fetch_books_by_category, name='fetch_books_by_category'),
]


