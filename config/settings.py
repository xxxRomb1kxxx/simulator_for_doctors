from dotenv import load_dotenv
import os
#pattern singleton
class Settings:
    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            load_dotenv()
            cls.__instance.BOT_TOKEN = os.getenv("BOT_TOKEN")
            cls.__instance.GIGA_CREDENTIALS = os.getenv("GIGA_CREDENTIALS")
            cls.__instance.SCOPE = os.getenv("SCOPE")
        return cls.__instance

settings = Settings()


