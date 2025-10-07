from dotenv import load_dotenv
import os

load_dotenv()  # loads .env file

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# OpenAI client setup
import openai
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = openai
openai_client.api_key = OPENAI_API_KEY
