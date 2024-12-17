# app/urls.py
from .views import RegisterView, LoginView, LogoutView
from django.urls import path,include
from . import views
from .views import search_books
from .views import list_users, list_books
from .views import create_user, update_user, delete_user
from .views import admin_dashboard, book_statistics, user_roles_statistics
from .views import create_user, update_user, delete_user,fetch_books_by_genre, edit_book_fields,delete_book
from .recommend_view import RecommendBooksAPIView
from rest_framework.routers import DefaultRouter



urlpatterns = [
    path('', views.home, name='home'),
    #Đăng ký
    path('api/register/', RegisterView.as_view(), name='register'),
    #Đăng nhập
    path('api/login/', LoginView.as_view(), name='login'),
    #Đăng xuất
    path('api/logout/', LogoutView.as_view(), name='logout'),
    #Tìm sách
    path('api/search-books/', search_books, name='search-books'), 
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
    
    #Recommend Book
    path('api/recommend_books/', RecommendBooksAPIView.as_view(), name='recommend_books'),


    path('user/profile/<int:user_id>/', views.get_user_profile, name='get-user-profile'),
    path('api/user/profile/update/<int:user_id>/', views.update_user_profile, name='update_user'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    path('api/favorites/add_to_favorites/', views.add_to_favorites, name='add_to_favorites'),
    path('api/favorites/remove_from_favorites/', views.remove_from_favorites, name='remove_from_favorites'),
    path('api/favorites/', views.get_favorites, name='get_favorites'),
    path('api/reading-history/add/', views.add_to_reading_history, name="add_to_reading_history"),
    path('api/reading-history/', views.get_reading_history, name="reading-history"),

    
    #===============================ADMIN==========================
    path('api/admin/users/', list_users, name='list_users'),
    path('api/admin/books/', list_books, name='list_books'),
    #update and delete user
    
    path('api/admin/users/create/', create_user, name='create_user'),
    path('api/admin/users/<int:user_id>/update/', update_user, name='update_user'),
    path('api/admin/users/<int:user_id>/delete/', delete_user, name='delete_user'),
    
    #add sach
    path('api/admin/fetch-books-genre/', fetch_books_by_genre, name='fetch_books_by_genre'),
    
    #edit,delete book
    path('api/books/<int:pk>/edit/', edit_book_fields, name='edit-book-fields'),
    path('api/books/<int:book_id>/delete/',delete_book, name='delete_book'),



]


