# app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    #Đăng ký
    path('api/register/', views.RegisterView.as_view(), name='register'),
    #Đăng nhập
    path('api/login/', views.LoginView.as_view(), name='login'),
    #Đăng xuất
    path('api/logout/', views.LogoutView.as_view(), name='logout'),
    #Quên Mật khẩu
    path('api/forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    #Tìm sách
    path('api/search-books/', views.search_books, name='search-books'), 
    #Tạo sách
    path('api/create-user-book/', views.create_user_book, name='create_user_book'),
    path('api/list-user-books/', views.list_user_books, name='list_user_books'),
    path('api/approve-user-book/<int:book_id>/', views.approve_user_book, name='approve_user_book'),
    #Trang Admin:
    path('api/admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('api/book-statistics/', views.book_statistics, name='book-statistics'),
    path('api/user-roles-statistics/', views.user_roles_statistics, name='user-roles-statistics'),
    #xem sach
    path('api/books/', views.all_books, name='all_books'),
    path('api/books/<int:book_id>/', views.book_detail_view, name='book_detail_view'),

    path('api/books/<int:book_id>/content/', views.book_content_by_id, name='book_content_by_id'),
    path('api/books/author/<str:author_name>/', views.books_by_author, name='books_by_author'),

    # API endpoints for reviews
    path('api/books/<int:book_id>/add_review/', views.add_review, name='add_review'),
    path('api/books/<int:book_id>/reviews/', views.get_book_reviews, name='get_book_reviews'),
    
    
    #admin
    path('api/admin/users/', views.list_users, name='list_users'),
    path('api/admin/books/', views.list_books, name='list_books'),
    
    path('api/admin/users/create/', views.create_user, name='create_user'),
    path('api/admin/users/<int:user_id>/update/', views.update_user, name='update_user'),
    path('api/admin/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    
    #add sach
    path('api/admin/fetch-books/', views.fetch_and_add_books, name='fetch_books'),
    #add book for gernes
    path('api/admin/fetch-books-gernes/', views.fetch_books_by_category, name='fetch_books_by_category'),
]


