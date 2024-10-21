from django.urls import path
from . import views
from .views import BookSearchAPIView

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/books/search/', BookSearchAPIView.as_view(), name='book-search'),
]

