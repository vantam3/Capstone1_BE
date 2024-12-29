from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Embedding, Book
from .serializers import BookSerializer
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from textblob import TextBlob
from langdetect import detect, LangDetectException

# Load BERT model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def validate_input(text):
    """
    Validate the input:
    - Detect the language using langdetect (only English is accepted).
    - Check for spelling errors using TextBlob.
    """
    try:
        lang = detect(text)
        if lang != "en":
            return False, "Input is not in English."
    except LangDetectException:
        return False, "Unable to detect the language of the input."

    # Check for spelling errors
    blob = TextBlob(text)
    corrected = str(blob.correct())
    if corrected != text:
        return False, f"Input contains spelling errors. Suggested correction: {corrected}"

    # If all checks are passed
    return True, None

def get_user_embedding(text):
    """
    Convert user preferences into embeddings using BERT model.
    Automatically truncate input if it exceeds 100 words.
    """
    words = text.split()
    if len(words) > 100:
        text = ' '.join(words[:100])

    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()
    return embedding[0]

class RecommendBooksAPIView(APIView):
    """
    API for recommending books based on user preferences.
    """
    def post(self, request):
        user_input = request.data.get('query', '')

        # Validate input
        is_valid, error_message = validate_input(user_input)
        if not is_valid:
            return Response({"error": error_message}, status=400)

        try:
            # Generate embedding from user preferences
            user_embedding = get_user_embedding(user_input)
        except Exception as e:
            return Response({"error": f"Failed to generate embedding: {str(e)}"}, status=500)

        try:
            # Fetch embeddings from the database
            embeddings = []
            books = []
            for embedding in Embedding.objects.all():
                try:
                    vector = json.loads(embedding.vector)
                    embeddings.append(vector)
                    books.append(embedding.book)
                except Exception as e:
                    print(f"Error decoding embedding {embedding.id}: {str(e)}")

            if not embeddings:
                return Response({"error": "No valid embeddings found in the database"}, status=500)

            # Convert the list of embeddings to a numpy array
            embeddings_array = np.array(embeddings)

            # Compute cosine similarity
            similarities = cosine_similarity([user_embedding], embeddings_array)[0]

            # Get top 5 recommended books
            top_indices = similarities.argsort()[-5:][::-1]
            recommended_books = [
                {"book": books[idx], "similarity": similarities[idx]} for idx in top_indices
            ]

            # Prepare the response data
            response_data = []
            for item in recommended_books:
                book = item["book"]
                similarity = item["similarity"]

                # Serialize each book
                serialized_book = BookSerializer(book).data

                # Add similarity score to book data
                serialized_book["similarity"] = similarity
                response_data.append(serialized_book)

            return Response(response_data)
        except Exception as e:
            return Response({"error": f"Failed to fetch recommendations: {str(e)}"}, status=500)
