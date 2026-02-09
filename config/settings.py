from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GIGA_CREDENTIALS = os.getenv("GIGA_CREDENTIALS")
SCOPE = os.getenv("SCOPE")

