import os
import re
import json
import logging
from datetime import datetime, date, timedelta

logger = logging.getLogger(__name__)


class WhisperService:
    """Service to handle Whisper speech-to-text with demo simulation and entity extraction."""

    def __init__(self, model_name="base"):
        self.model_name = model_name
        self._whisper_model = None
        self._is_available = None

    def is_available(self) -> bool:
        """Check if OpenAI Whisper library is installed and usable."""
        if self._is_available is not None:
            return self._is_available
        try:
            import whisper
            self._is_available = True
        except ImportError:
            self._is_available = False
        return self._is_available

    def transcribe_audio(self, audio_file_path: str = None, simulated_text: str = None) -> dict:
        """
        Transcribe an audio file using local Whisper if installed, 
        or use realistic demo transcriptions.
        """
        # If simulated_text was explicitly provided (e.g., from quick-presets or demo toggle)
        if simulated_text and simulated_text.strip():
            transcript = simulated_text.strip()
            mode = "Demo Preset Transcription"
        elif self.is_available() and audio_file_path and os.path.exists(audio_file_path):
            try:
                import whisper
                if self._whisper_model is None:
                    self._whisper_model = whisper.load_model(self.model_name)
                result = self._whisper_model.transcribe(audio_file_path)
                transcript = result.get('text', '').strip()
                mode = "Local Whisper STT"
            except Exception as e:
                logger.warning(f"Whisper inference error: {e}. Using demo fallback.")
                transcript = self._get_smart_fallback_text(audio_file_path)
                mode = "Demo Fallback Transcription"
        else:
            # Realistic Demo Transcription
            transcript = self._get_smart_fallback_text(audio_file_path)
            mode = "Demo Simulation Mode"

        # Extract structured entities
        entities = self.extract_entities(transcript)

        return {
            "transcript": transcript,
            "mode": mode,
            "entities": entities,
            "status": "success",
            "is_demo": (mode != "Local Whisper STT")
        }

    def _get_smart_fallback_text(self, audio_file_path: str = None) -> str:
        """Return realistic contextual transcriptions for demo demonstrations."""
        presets = [
            "Remind me to complete my internship application tomorrow at 10 AM.",
            "Add high priority task submit B.Tech minor project synopsis for College by tomorrow.",
            "Log fitness workout: Flat bench press 4 sets of 8 reps with 80 kg weight.",
            "Add coding task review pull request for ESP32 microphone I2S stream on GitHub."
        ]
        # Choose preset deterministically or based on second
        idx = datetime.now().second % len(presets)
        return presets[idx]

    def extract_entities(self, text: str) -> dict:
        """
        AI entity extraction to parse action type, dates, times, priorities,
        and categories from transcribed speech.
        """
        text_lower = text.lower()
        today = date.today()

        # 1. Action type
        if any(w in text_lower for w in ['remind', 'reminder', 'alarm', 'alert']):
            action_type = "Reminder"
        elif any(w in text_lower for w in ['workout', 'bench press', 'squat', 'gym', 'sets', 'reps', 'cardio']):
            action_type = "Workout"
        elif any(w in text_lower for w in ['task', 'todo', 'submit', 'complete', 'finish', 'prepare']):
            action_type = "Task"
        else:
            action_type = "Task"

        # 2. Priority detection
        if any(w in text_lower for w in ['urgent', 'asap', 'critical', 'immediately']):
            priority = "Urgent"
        elif any(w in text_lower for w in ['high', 'important', 'major']):
            priority = "High"
        elif any(w in text_lower for w in ['low', 'minor', 'later', 'someday']):
            priority = "Low"
        else:
            priority = "Medium"

        # 3. Category detection
        if any(w in text_lower for w in ['college', 'project', 'synopsis', 'exam', 'class', 'lab', 'b.tech', 'semester']):
            category = "College"
        elif any(w in text_lower for w in ['internship', 'interview', 'job', 'resume', 'recruiter', 'application']):
            category = "Internship"
        elif any(w in text_lower for w in ['code', 'coding', 'leetcode', 'bug', 'firmware', 'python', 'flask', 'ollama']):
            category = "Coding"
        elif any(w in text_lower for w in ['github', 'commit', 'pr', 'pull request', 'repo', 'branch']):
            category = "GitHub"
        elif any(w in text_lower for w in ['gym', 'workout', 'fitness', 'exercise', 'bench', 'squat', 'cardio']):
            category = "Fitness"
        else:
            category = "Personal"

        # 4. Date extraction
        target_date = today.isoformat()
        if 'tomorrow' in text_lower:
            target_date = (today + timedelta(days=1)).isoformat()
        elif 'day after tomorrow' in text_lower:
            target_date = (today + timedelta(days=2)).isoformat()
        elif 'next week' in text_lower:
            target_date = (today + timedelta(days=7)).isoformat()

        # 5. Time extraction (e.g. 10 AM, 4:30 PM, 16:00)
        time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.))', text, re.IGNORECASE)
        if time_match:
            time_str = time_match.group(1).upper()
        else:
            time_str = "10:00 AM"

        # 6. Title cleanup
        clean_title = re.sub(r'^(remind me to|add task|create task|schedule|please remind me to|add high priority task|add urgent task)\s*', '', text, flags=re.IGNORECASE)
        clean_title = re.sub(r'\s*(tomorrow|today|at \d{1,2}(?::\d{2})?\s*(?:am|pm)?|by \w+)\.?$', '', clean_title, flags=re.IGNORECASE).strip()
        if not clean_title:
            clean_title = text

        clean_title = clean_title.capitalize()

        # 7. Workout specific fields
        workout_data = {}
        if action_type == "Workout":
            sets_match = re.search(r'(\d+)\s*sets', text_lower)
            reps_match = re.search(r'(\d+)\s*reps', text_lower)
            weight_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kgs|kilos|pounds|lbs)', text_lower)
            
            workout_data = {
                'exercise_name': clean_title or 'Strength Training',
                'sets': int(sets_match.group(1)) if sets_match else 4,
                'reps': int(reps_match.group(1)) if reps_match else 8,
                'weight': float(weight_match.group(1)) if weight_match else 75.0,
                'duration_minutes': 45,
                'calories_burned': 260
            }

        return {
            "action_type": action_type,
            "title": clean_title,
            "category": category,
            "priority": priority,
            "date": target_date,
            "time": time_str,
            "workout": workout_data
        }


whisper_service = WhisperService()
