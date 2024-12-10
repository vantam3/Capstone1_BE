from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Embedding, Book
from .serializers import BookSerializer
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pickle

# Tải mô hình BERT
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Hàm tạo embedding từ văn bản
def get_user_embedding(text):
    """
    Chuyển sở thích người dùng thành embedding sử dụng mô hình BERT.
    Tự động cắt ngắn đầu vào nếu vượt quá 50 từ.
    """
    words = text.split()
    if len(words) > 50:
        text = ' '.join(words[:50])  # Giữ lại 50 từ đầu tiên

    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()
    return embedding[0]

class RecommendBooksAPIView(APIView):
    """
    API để gợi ý sách dựa trên sở thích người dùng, trả về thông tin sách và điểm tương đồng.
    """
    def post(self, request):
        # Lấy dữ liệu từ body của POST request
        user_input = request.data.get('query', '')

        if not user_input:
            return Response({"error": "Missing 'query' parameter in request body"}, status=400)

        try:
            # Tạo embedding từ sở thích người dùng
            user_embedding = get_user_embedding(user_input)
        except Exception as e:
            return Response({"error": f"Failed to generate embedding: {str(e)}"}, status=400)

        try:
            # Lấy embedding từ database
            embeddings = []
            books = []
            for embedding in Embedding.objects.all():
                vector = pickle.loads(embedding.vector)  # Giải mã nhị phân
                embeddings.append(vector)
                books.append(embedding.book)

            # Chuyển danh sách embedding thành numpy array
            embeddings_array = np.array(embeddings)

            # Tính độ tương đồng cosine
            similarities = cosine_similarity([user_embedding], embeddings_array)[0]

            # Lấy top 5 sách gợi ý
            top_indices = similarities.argsort()[-5:][::-1]
            recommended_books = [
                {"book": books[idx], "similarity": similarities[idx]} for idx in top_indices
            ]

            # Chuẩn bị dữ liệu trả về
            response_data = []
            for item in recommended_books:
                book = item["book"]
                similarity = item["similarity"]

                # Serialize từng sách
                serialized_book = BookSerializer(book).data

                # Thêm điểm tương đồng vào dữ liệu sách
                serialized_book["similarity"] = similarity
                response_data.append(serialized_book)

            return Response(response_data)
        except Exception as e:
            return Response({"error": f"Failed to fetch recommendations: {str(e)}"}, status=500)
