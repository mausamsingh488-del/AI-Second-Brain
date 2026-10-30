import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables if .env exists
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


class Config:
    """Application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ai-second-brain-ultra-secure-key-2026')

    # Paths
    BASE_DIR = BASE_DIR
    DATABASE_DIR = BASE_DIR / 'database'
    UPLOAD_FOLDER = BASE_DIR / 'uploads'

    # Ensure required directories exist
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    # SQLite Database URI (using forward slashes for cross-platform SQLite)
    db_path = DATABASE_DIR / 'second_brain.db'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f'sqlite:///{db_path.as_posix()}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm', 'm4a'}

    # Demo & Hardware Simulation settings
    DEMO_MODE = os.environ.get('DEMO_MODE', 'True').lower() in ('true', '1', 't', 'yes')

    # AI Configuration (Local Ollama & Whisper)
    OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3')
    WHISPER_MODEL = os.environ.get('WHISPER_MODEL', 'base')

    # ESP32 Device Configuration
    ESP32_IP = os.environ.get('ESP32_IP', '192.168.1.150')
    ESP32_PORT = int(os.environ.get('ESP32_PORT', 80))

    # GitHub integration
    GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME', 'mausam-dev')
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

    # Theme colors requested by user
    THEME_COLORS = {
        'primary': '#D5851F',      # Warm Amber / Ochre Gold
        'secondary': '#87A96B',    # Asparagus / Cyber Sage Green
        'dark': '#5A3E2B',         # Deep Bistro / Warm Dark Brown
        'bg_dark': '#13110F',      # Obsidian Warm Dark Base
        'card_bg': 'rgba(42, 31, 23, 0.72)'
    }
