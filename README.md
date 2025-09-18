# Capstone1_BE
# BookQuest - Backend Documentation

## 📚 Tổng quan dự án (Project Overview)

**BookQuest** là một hệ thống backend để quản lý sách điện tử, được xây dựng như một dự án capstone. Hệ thống tập trung vào việc cung cấp sách miễn phí từ Project Gutenberg và cho phép người dùng tương tác với nội dung sách thông qua các tính năng như yêu thích, lịch sử đọc, đánh giá và gợi ý sách.

### 🎯 Mục tiêu chính
- Tự động thu thập sách từ Project Gutenberg
- Quản lý tương tác người dùng (yêu thích, lịch sử đọc, đánh giá)
- Hệ thống gợi ý sách thông minh sử dụng AI
- Quản lý sách do cộng đồng tạo ra
- Cung cấp API RESTful cho frontend

## 🏗️ Kiến trúc hệ thống (System Architecture)

### Tech Stack
- **Backend Framework**: Django 5.1.1
- **Database**: MySQL
- **API Framework**: Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **AI/ML**: BERT model cho gợi ý sách
- **Email Service**: Gmail SMTP
- **CORS**: django-cors-headers

### Cấu trúc thư mục
```
book_web/
├── app/                          # Main application
│   ├── data/                     # Downloaded books data files
│   ├── management/commands/      # Django management commands
│   │   └── fetch_gutenberg_books.py
│   ├── migrations/               # Database migrations
│   ├── models.py                 # Database models
│   ├── views.py                  # API views
│   ├── serializers.py            # DRF serializers
│   ├── urls.py                   # URL routing
│   ├── admin.py                  # Django admin configuration
│   ├── recommend_view.py         # AI recommendation system
│   └── tests.py                  # Unit tests
├── book_web/                     # Project configuration
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Main URL configuration
│   ├── wsgi.py                   # WSGI configuration
│   └── asgi.py                   # ASGI configuration
└── manage.py                     # Django management script
```

## 📊 Mô hình dữ liệu (Database Models)

### 1. Book Model
```python
class Book(models.Model):
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=255, null=True, blank=True)
    download_link = models.TextField(null=True, blank=True)
    gutenberg_id = models.IntegerField(unique=True)
    image = models.URLField(default='https://example.com/default-image.jpg', blank=True)
    subject = models.TextField(null=True, blank=True)
    isbn = models.CharField(max_length=13, unique=True, null=True, blank=True)
    language = models.CharField(max_length=20, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    genres = models.ManyToManyField(Genre, related_name='books')
```

### 2. User Interaction Models
- **Review**: Đánh giá và bình luận sách
- **FavoriteBook**: Sách yêu thích của người dùng
- **ReadingHistory**: Lịch sử đọc sách
- **UserBook**: Sách do người dùng tạo

### 3. AI/ML Models
- **Embedding**: Lưu trữ vector embeddings cho hệ thống gợi ý
- **Genre**: Phân loại sách theo thể loại

## 🔧 Các tính năng chính (Core Features)

### 1. Authentication & User Management
- **Đăng ký/Đăng nhập**: JWT-based authentication
- **Quên mật khẩu**: Email verification với mã xác nhận
- **Quản lý profile**: Cập nhật thông tin cá nhân
- **Phân quyền**: Admin và user thông thường

### 2. Book Management
- **Tự động thu thập**: Fetch sách từ Project Gutenberg API
- **CRUD operations**: Tạo, đọc, cập nhật, xóa sách
- **Tìm kiếm**: Theo tiêu đề, tác giả
- **Phân loại**: Theo thể loại (genres)

### 3. User Interactions
- **Yêu thích**: Thêm/xóa sách khỏi danh sách yêu thích
- **Lịch sử đọc**: Theo dõi sách đã đọc
- **Đánh giá**: Rating (1-5 sao) và bình luận
- **Sách cá nhân**: Người dùng có thể tạo sách riêng

### 4. AI Recommendation System
- **BERT-based**: Sử dụng mô hình BERT để tạo embeddings
- **Cosine Similarity**: Tính toán độ tương tự
- **Multilingual Support**: Kiểm tra ngôn ngữ đầu vào
- **Spell Check**: Kiểm tra chính tả

### 5. Admin Dashboard
- **Thống kê**: Số liệu về sách, người dùng, đánh giá
- **Quản lý người dùng**: CRUD operations
- **Quản lý sách**: Duyệt sách từ cộng đồng
- **Fetch sách**: Tự động thêm sách theo thể loại

## 🚀 API Endpoints

### Authentication
```
POST /api/register/              # Đăng ký
POST /api/login/                 # Đăng nhập
POST /api/logout/                # Đăng xuất
POST /api/forgot-password/       # Quên mật khẩu
POST /api/reset-password/        # Đặt lại mật khẩu
```

### Books
```
GET  /api/books/                           # Lấy tất cả sách
GET  /api/books/<id>/                      # Chi tiết sách
GET  /api/books/<id>/content/              # Nội dung sách
GET  /api/books/author/<author_name>/      # Sách theo tác giả
GET  /api/search-books/?q=<query>          # Tìm kiếm sách
```

### User Interactions
```
POST /api/books/<id>/add_review/           # Thêm đánh giá
GET  /api/books/<id>/reviews/              # Lấy đánh giá
POST /api/favorites/add_to_favorites/      # Thêm yêu thích
POST /api/favorites/remove_from_favorites/ # Xóa yêu thích
GET  /api/favorites/                       # Danh sách yêu thích
POST /api/reading-history/add/             # Thêm lịch sử đọc
GET  /api/reading-history/                 # Lấy lịch sử đọc
```

### AI Recommendations
```
POST /api/recommend_books/                 # Gợi ý sách
```

### User Books (Community Content)
```
POST /api/create-user-book/                # Tạo sách mới
GET  /api/list-user-books/                 # Sách chờ duyệt (Admin)
GET  /api/list-approved-books/             # Sách đã duyệt
PUT  /api/approve-user-book/<id>/          # Duyệt sách (Admin)
DELETE /api/reject-delete-book/<id>/       # Từ chối sách (Admin)
```

### Admin Dashboard
```
GET  /api/admin_dashboard/                 # Dashboard chính
GET  /api/book-statistics/                 # Thống kê sách
GET  /api/user-roles-statistics/           # Thống kê người dùng
GET  /api/rating-statistics/               # Thống kê đánh giá
GET  /api/report-statistics/               # Báo cáo tổng hợp
```

## ⚙️ Cài đặt và triển khai (Setup & Deployment)

### Yêu cầu hệ thống
- Python 3.8+
- MySQL 8.0+
- Django 5.1.1
- Node.js (cho frontend)

### Cài đặt Backend

1. **Clone repository**
```bash
git clone <repository-url>
cd Capstone1_BE
```

2. **Tạo virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Cài đặt dependencies** (Cần tạo requirements.txt)
```bash
pip install django
pip install djangorestframework
pip install django-cors-headers
pip install djangorestframework-simplejwt
pip install mysqlclient
pip install transformers
pip install scikit-learn
pip install textblob
pip install langdetect
pip install numpy
pip install torch
pip install beautifulsoup4
pip install requests
```

4. **Cấu hình database**
- Tạo database MySQL tên `book_web`
- Cập nhật thông tin kết nối trong `settings.py`

5. **Chạy migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Tạo superuser**
```bash
python manage.py createsuperuser
```

7. **Thu thập sách từ Project Gutenberg**
```bash
python manage.py fetch_gutenberg_books --size=50
```

8. **Chạy server**
```bash
python manage.py runserver
```

### Cấu hình Email (Gmail SMTP)
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## 🤖 Hệ thống AI Recommendation

### Cách hoạt động
1. **Text Processing**: Xử lý và validate input từ người dùng
2. **Embedding Generation**: Sử dụng BERT để tạo vector embeddings
3. **Similarity Calculation**: Tính cosine similarity với embeddings có sẵn
4. **Ranking**: Sắp xếp và trả về top 5 sách phù hợp nhất

### Input Validation
- Kiểm tra ngôn ngữ (chỉ tiếng Anh)
- Kiểm tra chính tả
- Giới hạn độ dài input (100 từ)

### Sử dụng
```python
POST /api/recommend_books/
{
    "query": "science fiction space adventure"
}
```

## 🔒 Bảo mật (Security)

### Authentication
- JWT tokens với thời gian hết hạn
- Token blacklisting khi logout
- Password hashing với Django's built-in system

### Data Protection
- Input validation và sanitization
- SQL injection protection (Django ORM)
- CORS configuration
- CSRF protection

### Admin Features
- Role-based access control
- Admin-only endpoints
- User management capabilities

## 📈 Monitoring & Analytics

### Database Statistics
- Số lượng sách theo thể loại
- Thống kê người dùng theo vai trò
- Phân tích đánh giá và rating
- Báo cáo tổng hợp hoạt động

### Performance Monitoring
- Cache configuration (LocMem)
- Database query optimization
- API response time tracking

## 🧪 Testing

### Test Structure
- Unit tests cho models
- API endpoint testing
- Authentication flow testing
- Recommendation system testing

### Chạy tests
```bash
python manage.py test
```

## 📝 Management Commands

### fetch_gutenberg_books
```bash
python manage.py fetch_gutenberg_books --size=20 --max_page=100
```
- Tự động fetch sách từ Project Gutenberg
- Lưu vào database mà không tạo duplicate
- Chỉ lấy sách có hình ảnh

## 🚀 Deployment Notes

### Production Settings
- Đặt `DEBUG = False`
- Cấu hình `ALLOWED_HOSTS`
- Sử dụng production database
- Setup static files serving
- Configure logging

### Recommended Infrastructure
- **Web Server**: Nginx
- **Application Server**: Gunicorn
- **Database**: MySQL/PostgreSQL
- **Caching**: Redis (production)
- **File Storage**: AWS S3 (production)

## 🔄 Future Enhancements

### Planned Features
1. **Advanced Search**: Elasticsearch integration
2. **Social Features**: User following, book clubs
3. **Mobile API**: Optimized endpoints cho mobile app
4. **Real-time Notifications**: WebSocket support
5. **Advanced Analytics**: User behavior tracking
6. **Content Moderation**: AI-powered content filtering
7. **Internationalization**: Multi-language support

### Performance Improvements
- Database indexing optimization
- API caching strategies
- CDN integration
- Background task processing (Celery)

## 📞 Support & Contact

### Development Team
- Project: Capstone1_BE
- Framework: Django 5.1.1
- Database: MySQL
- Documentation Updated: 2024-12-17

### Common Issues & Solutions
1. **Database Connection**: Kiểm tra MySQL service và credentials
2. **CORS Errors**: Cấu hình CORS_ALLOWED_ORIGINS
3. **JWT Errors**: Kiểm tra token expiry và blacklist
4. **Email Issues**: Verify Gmail app password
5. **AI Model Loading**: Ensure sufficient memory for BERT model

---

*Tài liệu này cung cấp cái nhìn tổng quan về dự án BookQuest Backend. Để biết thêm chi tiết, vui lòng tham khảo source code và comments trong các file.*