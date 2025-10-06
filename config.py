import os
import logging
from dotenv import load_dotenv

load_dotenv()


def setup_logging_globally():
    """Настраивает глобальное логирование"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("bot.log", encoding="utf-8"),
        ],
    )


# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# GigaChat Settings
GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS")
GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
GIGACHAT_VERIFY_SSL_CERTS = (
    os.getenv("GIGACHAT_VERIFY_SSL_CERTS", "False").lower() == "true"
)
GIGACHAT_MODEL = os.getenv("GIGACHAT_MODEL", "GigaChat-Max")
GIGACHAT_TIMEOUT = int(os.getenv("GIGACHAT_TIMEOUT", "30"))
GIGACHAT_PROFANITY_CHECK = (
    os.getenv("GIGACHAT_PROFANITY_CHECK", "False").lower() == "true"
)
GIGACHAT_TEMPERATURE = float(os.getenv("GIGACHAT_TEMPERATURE", "0.3"))
GIGACHAT_MAX_TOKENS = int(os.getenv("GIGACHAT_MAX_TOKENS", "500"))

# FusionBrain (Kandinsky) Settings
FUSIONBRAIN_URL = os.getenv("FUSIONBRAIN_URL", "https://api-key.fusionbrain.ai/")
FUSIONBRAIN_API_KEY = os.getenv("FUSIONBRAIN_API_KEY")
FUSIONBRAIN_SECRET_KEY = os.getenv("FUSIONBRAIN_SECRET_KEY")
