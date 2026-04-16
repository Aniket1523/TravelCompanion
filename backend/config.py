import os

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
RATE_LIMIT: str = os.getenv("RATE_LIMIT", "60/minute")
