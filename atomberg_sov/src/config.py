"""Configuration module for the SoV analyzer"""
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Search Configuration
NUM_RESULTS = int(os.getenv("NUM_RESULTS", 20))
SENTIMENT_THRESHOLD = float(os.getenv("SENTIMENT_THRESHOLD", 0.5))
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "html")

# Atomberg and competitors
ATOMBERG_KEYWORDS = ["atomberg", "smart fan atomberg", "atomberg ceiling fan"]
COMPETITOR_KEYWORDS = ["havells", "orient", "ortem", "agni", "carro", "luminous"]

# Platform-specific settings
PLATFORMS = {
    "mock": {"enabled": True, "weight": 1.0},
}

# Keywords to analyze
SEARCH_KEYWORDS = [
    "smart fan",
    "smart ceiling fan",
    "WiFi controlled fan",
]

# API Keys (optional)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
