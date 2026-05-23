"""
config.py — Central configuration for ResearchPilot AI.
All settings are read from environment variables (your .env file).
"""

import os
from dotenv import load_dotenv

# Load the .env file so os.getenv() can see your keys
load_dotenv()


class Config:
    """Base config shared by all environments."""

    # Flask needs a secret key to sign session cookies
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

    # Gemini API key — required for all AI agents
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # Which Gemini model to use (flash is fast & cheap, good for hackathons)
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # How many arXiv papers to fetch per research query
    ARXIV_MAX_RESULTS = int(os.getenv("ARXIV_MAX_RESULTS", 5))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# Map string names → config classes so run.py can pick one
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
