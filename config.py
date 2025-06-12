import os
from dotenv import load_dotenv

load_dotenv()

GPT_TOKEN = os.getenv("GPT_TOKEN")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")

if not all([GPT_TOKEN, TG_BOT_TOKEN]):
    raise ValueError("Missing tokens, check .env.example file")