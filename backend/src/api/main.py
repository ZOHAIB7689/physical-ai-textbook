from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from backend.src.utils.logger import setup_logging
from backend.src.api.modules import router as modules_router
from backend.src.api.chapters import router as chapters_router
from backend.src.api.users import router as users_router
from backend.src.api.ai import router as ai_router
from backend.src.api.content_management import router as content_management_router
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

def create_app() -> FastAPI:
    app = FastAPI(
        title="Physical AI & Humanoid Robotics Textbook Platform API",
        description="API for the AI-Native Textbook Platform for Physical AI & Humanoid Robotics",
        version="1.0.0"
    )

    # Add security headers middleware
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=os.getenv("ALLOWED_HOSTS", "*").split(","))

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost,http://localhost:3000").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # Additional security-related headers
        allow_origin_regex=os.getenv("ALLOW_ORIGIN_REGEX", None),
        # Expose headers that browsers are allowed to access
        expose_headers=["Access-Control-Allow-Origin"]
    )

    # Include API routers
    app.include_router(users_router, prefix="/api", tags=["users"])
    app.include_router(modules_router, prefix="/api", tags=["modules"])
    app.include_router(chapters_router, prefix="/api", tags=["chapters"])
    app.include_router(ai_router, prefix="/api", tags=["ai"])
    app.include_router(content_management_router, prefix="/api", tags=["content_management"])

    return app

# Create the main application instance
app = create_app()

@app.get("/")
def read_root():
    return {"message": "Physical AI & Humanoid Robotics Textbook Platform API"}