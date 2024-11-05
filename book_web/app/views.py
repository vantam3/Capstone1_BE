from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from rest_framework import generics, permissions
from .models import Book, Review
from .serializers import BookSerializer, ReviewSerializer, BookDetailSerializer
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework import status

def home(request):
    return HttpResponse("Bookquest")
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Đăng ký thành công!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'app/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Đăng nhập thành công!')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'app/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('login')

class BookSearchAPIView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [SearchFilter]
    search_fields = ['title', 'author', 'language']  # Cho phép tìm kiếm theo tiêu đề, tác giả và ngôn ngữ

class BookDetailAPIView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer

class ReviewCreateAPIView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]  # Chỉ người dùng đã đăng nhập mới có thể thêm đánh giá

    def perform_create(self, serializer):
        book_id = self.request.data.get('book')  # Lấy book ID từ request data
        book = generics.get_object_or_404(Book, pk=book_id)  # Kiểm tra xem sách có tồn tại không
        serializer.save(user=self.request.user, book=book)  # Lưu review với thông tin user và book

