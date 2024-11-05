from django.urls import path
from . import views
from .views import BookSearchAPIView, BookDetailAPIView, ReviewCreateAPIView

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/books/search/', BookSearchAPIView.as_view(), name='book-search'), #Tìm sách
    path('api/books/<int:pk>/', BookDetailAPIView.as_view(), name='book-detail'),  # Xem chi tiết sách và các đánh giá
    path('api/reviews/', ReviewCreateAPIView.as_view(), name='review-create'),  # Tạo đánh giá mới
]

