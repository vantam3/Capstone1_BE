from openai import OpenAI
import os
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def ask_mistral(user_input):
    try:
        response = client.chat.completions.create(
            model="mistral-saba-24b",
            # model="mistral-7b-instruct-v0.1",  # Uncomment if you want to use the smaller model
            messages=[
                {"role": "system", "content": "You are a helpful book advisor who recommends books based on the user's interests, like a personal reading consultant."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=2048
        )
        reply = response.choices[0].message.content
        print("[✔] Phản hồi từ Groq:", reply)
        return reply
    except Exception as e:
        print("[❌] Lỗi gọi Groq API:", str(e))
        return "Sorry, I could not respond at the moment."
