import os
from dotenv import load_dotenv

load_dotenv()


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_API_PORT=os.getenv("RABBITMQ_API_PORT" , "15672" )


SELECTOR_LAMBDA_URL=os.getenv("SELECTOR_LAMBDA_URL")
SCRAPER_LAMBDA_URL=os.getenv("SCRAPER_LAMBDA_URL")
AI_RATE_LIMITER_URL=os.getenv("AI_RATE_LIMITER_URL")

API_BASE_URL=os.getenv("API_BASE_URL")
API_EMAIL=os.getenv("API_EMAIL")
API_PASSWORD=os.getenv("API_PASSWORD")