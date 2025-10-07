import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def score_answer(question: str, answer: str) -> int:
    prompt = f"Score this answer out of 10.\nQuestion: {question}\nAnswer: {answer}\nScore:"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    score_text = response.choices[0].message.content.strip()
    try:
        return int(score_text)
    except:
        return 0
