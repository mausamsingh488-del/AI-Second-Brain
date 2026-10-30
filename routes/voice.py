import os
import json
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from datetime import datetime, date
from models.models import db, VoiceNote, Conversation, Task, Reminder, Workout
from services.whisper_service import whisper_service
from services.ollama_service import ollama_service
from services.esp32_service import esp32_service
from services.github_service import github_service

voice_bp = Blueprint('voice', __name__, url_prefix='/api')


# ==================== VOICE TRANSCRIPTION & PROCESSING ====================

@voice_bp.route('/voice/transcribe', methods=['POST'])
def transcribe_voice():
    """Handle audio upload or preset simulation, transcribing speech to structured data."""
    try:
        audio_path = None
        simulated_text = None

        # Check if multipart form with audio file
        if 'audio' in request.files:
            audio_file = request.files['audio']
            if audio_file.filename != '':
                filename = secure_filename(f"voice_{int(datetime.now().timestamp())}_{audio_file.filename}")
                upload_dir = current_app.config['UPLOAD_FOLDER']
                audio_path = os.path.join(upload_dir, filename)
                audio_file.save(audio_path)

        # Check if JSON payload (simulated preset or direct text)
        if request.is_json:
            data = request.get_json() or {}
            simulated_text = data.get('simulated_text')

        # Transcribe through Whisper service
        result = whisper_service.transcribe_audio(
            audio_file_path=audio_path,
            simulated_text=simulated_text
        )

        return jsonify({
            "status": "success",
            "transcript": result['transcript'],
            "mode": result['mode'],
            "entities": result['entities'],
            "is_demo": result['is_demo'],
            "audio_path": audio_path
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@voice_bp.route('/voice/save', methods=['POST'])
def save_voice_note():
    """Save voice note and optionally auto-create task, reminder, or workout."""
    try:
        data = request.get_json() or {}
        transcript = data.get('transcript', '').strip()
        if not transcript:
            return jsonify({"status": "error", "message": "Transcript is empty"}), 400

        entities = data.get('entities') or {}
        action_type = entities.get('action_type', 'Task')
        auto_create = data.get('auto_create', True)

        # 1. Save VoiceNote
        note = VoiceNote(
            transcript=transcript,
            original_audio_path=data.get('audio_path'),
            action_type=action_type,
            extracted_data=json.dumps(entities),
            status='Processed',
            duration_seconds=data.get('duration_seconds', 5)
        )
        db.session.add(note)

        created_item = None

        # 2. Automatically spawn record if requested
        if auto_create:
            if action_type == 'Reminder':
                rem = Reminder(
                    title=entities.get('title') or transcript,
                    description=f"Voice Note: {transcript}",
                    reminder_date=entities.get('date') or date.today().isoformat(),
                    reminder_time=entities.get('time', '10:00 AM'),
                    priority=entities.get('priority', 'Medium'),
                    status='Today' if entities.get('date') == date.today().isoformat() else 'Upcoming'
                )
                db.session.add(rem)
                created_item = {'type': 'Reminder', 'title': rem.title}

            elif action_type == 'Workout':
                w_data = entities.get('workout') or {}
                workout = Workout(
                    exercise_name=w_data.get('exercise_name') or 'Strength Session',
                    category='Strength',
                    sets=w_data.get('sets', 4),
                    reps=w_data.get('reps', 8),
                    weight=w_data.get('weight', 75.0),
                    duration_minutes=w_data.get('duration_minutes', 45),
                    calories_burned=w_data.get('calories_burned', 260),
                    workout_date=entities.get('date') or date.today().isoformat(),
                    notes=f"Logged via voice: '{transcript}'"
                )
                db.session.add(workout)
                created_item = {'type': 'Workout', 'exercise': workout.exercise_name}

            else:  # Task
                task = Task(
                    title=entities.get('title') or transcript,
                    description=f"Captured via Second-Brain voice: \"{transcript}\"",
                    category=entities.get('category', 'Personal'),
                    priority=entities.get('priority', 'Medium'),
                    due_date=entities.get('date') or date.today().isoformat(),
                    completed=False
                )
                db.session.add(task)
                created_item = {'type': 'Task', 'title': task.title}

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Voice note saved and processed into your Second Brain!",
            "voice_note": note.to_dict(),
            "created_item": created_item
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@voice_bp.route('/voice/notes', methods=['GET'])
def get_voice_notes():
    """Retrieve history of captured voice notes."""
    try:
        notes = VoiceNote.query.order_by(VoiceNote.id.desc()).all()
        return jsonify({
            "status": "success",
            "count": len(notes),
            "notes": [n.to_dict() for n in notes]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==================== AI BRAIN CHAT ====================

@voice_bp.route('/ai/chat', methods=['POST'])
def ai_chat():
    """Handle chat interaction with Ollama or Demo AI fallback."""
    try:
        data = request.get_json() or {}
        user_message = data.get('message', '').strip()
        model_name = data.get('model')

        if not user_message:
            return jsonify({"status": "error", "message": "Message cannot be empty"}), 400

        # Fetch recent conversation context (last 6 messages)
        recent_chats = Conversation.query.order_by(Conversation.id.desc()).limit(6).all()
        history = [{'role': c.role, 'message': c.message} for c in reversed(recent_chats)]

        # Save user message
        user_record = Conversation(role='user', message=user_message, mode='user', model_used=model_name or 'user')
        db.session.add(user_record)

        # Generate AI response
        ai_result = ollama_service.generate_chat_response(
            prompt=user_message,
            conversation_history=history,
            model=model_name
        )

        bot_text = ai_result['text']
        mode_str = ai_result['mode']
        model_used = ai_result['model']

        # Save assistant message
        bot_record = Conversation(
            role='assistant',
            message=bot_text,
            mode=mode_str,
            model_used=model_used
        )
        db.session.add(bot_record)
        db.session.commit()

        return jsonify({
            "status": "success",
            "response": bot_text,
            "mode": mode_str,
            "model": model_used,
            "is_demo": ai_result['is_demo']
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@voice_bp.route('/ai/history', methods=['GET'])
def get_ai_history():
    """Retrieve conversation history."""
    try:
        convo = Conversation.query.order_by(Conversation.id.asc()).all()
        return jsonify({
            "status": "success",
            "messages": [c.to_dict() for c in convo]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@voice_bp.route('/ai/clear', methods=['POST'])
def clear_ai_history():
    """Clear conversation history."""
    try:
        Conversation.query.delete()
        db.session.commit()
        return jsonify({"status": "success", "message": "AI conversation history cleared!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


# ==================== ESP32 HARDWARE DEVICE ====================

@voice_bp.route('/device/status', methods=['GET'])
def get_device_status():
    """Retrieve live ESP32 status and telemetry."""
    status_data = esp32_service.get_status()
    return jsonify({"status": "success", "device": status_data})


@voice_bp.route('/device/action', methods=['POST'])
def perform_device_action():
    """Execute hardware actions (test mic, test LCD, sync, restart, toggle)."""
    try:
        data = request.get_json() or {}
        action = data.get('action')

        if action == 'test_mic':
            res = esp32_service.test_microphone()
        elif action == 'test_lcd':
            text = data.get('text', 'AI Second Brain: Active!')
            res = esp32_service.update_lcd(text)
        elif action == 'sync':
            res = esp32_service.sync_time()
        elif action == 'restart':
            res = esp32_service.restart()
        elif action == 'toggle':
            res = esp32_service.toggle_connection()
        else:
            return jsonify({"status": "error", "message": f"Unknown action: {action}"}), 400

        # Refresh full status after action
        res['device'] = esp32_service.get_status()
        return jsonify(res)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==================== GITHUB INTEGRATION ====================

@voice_bp.route('/github', methods=['GET'])
def get_github_data():
    """Fetch GitHub profile, repositories, and heatmap."""
    username = request.args.get('username') or current_app.config.get('GITHUB_USERNAME', 'mausam-dev')
    data = github_service.get_profile_data(username)
    return jsonify({"status": "success", "github": data})
