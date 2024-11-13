# app/urls.py
from .views import register_user, login_user
from django.urls import path
from . import views
from .views import BookSearchAPIView

urlpatterns = [
    path('', views.home, name='home'),
    #Đăng ký
    path('api/register/', register_user, name='register_user'),
    #Đăng nhập
    path('api/login/', login_user, name='login_user'),
    #Tìm sách
    path('api/books/search/', BookSearchAPIView.as_view(), name='book-search'), 
    #xem sach
    path('api/books/', views.all_books, name='all_books'),
    #doc sach
    path('api/books/<slug:slug>/', views.book_content_by_slug, name='book_content_by_slug'),
    #xem sach theo author
    path('api/books/author/<str:author_name>/', views.books_by_author, name='books_by_author'),
    #them rating va comment
    path('api/book/<int:book_id>/add_review/', views.add_review, name='add_review'),
    #xem reviews
    path('api/book/<int:book_id>/reviews/', views.get_book_reviews, name='get_book_reviews'),

]
