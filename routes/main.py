from flask import Blueprint, render_template, current_app
from models.models import Task, Reminder, Habit, Workout, VoiceNote, Device, Setting, Conversation
from services.ollama_service import ollama_service
from services.whisper_service import whisper_service
from services.esp32_service import esp32_service
from services.github_service import github_service

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page showcasing the AI Second-Brain concept."""
    return render_template('index.html')


@main_bp.route('/dashboard')
def dashboard():
    """Central Control Dashboard."""
    return render_template('dashboard.html')


@main_bp.route('/brain')
def brain():
    """AI Brain Chat interface."""
    return render_template('brain.html')


@main_bp.route('/voice')
def voice():
    """Voice Assistant recording and transcription console."""
    return render_template('voice.html')


@main_bp.route('/tasks')
def tasks():
    """Smart Task Management."""
    return render_template('tasks.html')


@main_bp.route('/reminders')
def reminders():
    """Time-sensitive Reminders."""
    return render_template('reminders.html')


@main_bp.route('/habits')
def habits():
    """Habit Tracker with streaks."""
    return render_template('habits.html')


@main_bp.route('/github')
def github():
    """GitHub activity, repositories, and contribution heatmap."""
    return render_template('github.html')


@main_bp.route('/fitness')
def fitness():
    """Fitness and Gym tracking log."""
    return render_template('fitness.html')


@main_bp.route('/analytics')
def analytics():
    """Deep productivity and activity analytics."""
    return render_template('analytics.html')


@main_bp.route('/device')
def device():
    """ESP32 Hardware status and testing station."""
    return render_template('device.html')


@main_bp.route('/settings')
def settings():
    """System settings and configurations."""
    return render_template('settings.html')


@main_bp.route('/download-zip')
def download_zip():
    """Download the complete project ZIP archive."""
    from flask import send_file
    import os
    zip_path = os.path.abspath(os.path.join(current_app.config['BASE_DIR'], '..', 'AI-Second-Brain.zip'))
    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True, download_name='AI-Second-Brain.zip')
    return "ZIP archive not found", 404

