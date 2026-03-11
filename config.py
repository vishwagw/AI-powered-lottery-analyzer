"""
Configuration settings for Lottery Analyzer
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent

# Database configuration
DB_PATH = PROJECT_ROOT / "data" / "lottery.db"
DB_NAME = "lottery.db"

# Website URLs
DLB_URL = "https://www.dlb.lk/"
NLB_URL = "https://www.nlb.lk/"

# Scraper settings
TIMEOUT = 15
MAX_RETRIES = 3
HEADLESS_BROWSER = True

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = DATA_DIR / "results"

# Create necessary directories
DATA_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)
