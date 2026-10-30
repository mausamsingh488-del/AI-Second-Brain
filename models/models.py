from datetime import datetime, date, timedelta
import json
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """User profile model."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, default='Mausam')
    email = db.Column(db.String(120), unique=True, nullable=False, default='mausam@secondbrain.ai')
    full_name = db.Column(db.String(120), default='Mausam (B.Tech CSE)')
    bio = db.Column(db.Text, default='AI researcher & student building smart hardware second brain.')
    avatar_url = db.Column(db.String(255), default='https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=256&q=80')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Task(db.Model):
    """Smart Task model with categories and priorities."""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    category = db.Column(db.String(50), nullable=False, default='General')  # College, Internship, Coding, Personal, Fitness, GitHub
    priority = db.Column(db.String(20), nullable=False, default='Medium')    # Low, Medium, High, Urgent
    due_date = db.Column(db.String(50), nullable=True)                      # YYYY-MM-DD or formatted string
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'due_date': self.due_date,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Reminder(db.Model):
    """Time-sensitive Reminder model."""
    __tablename__ = 'reminders'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    reminder_date = db.Column(db.String(50), nullable=False)  # YYYY-MM-DD
    reminder_time = db.Column(db.String(20), nullable=False)  # HH:MM (24-hour)
    priority = db.Column(db.String(20), default='Medium')
    status = db.Column(db.String(20), default='Upcoming')     # Upcoming, Today, Completed, Overdue
    notified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'reminder_date': self.reminder_date,
            'reminder_time': self.reminder_time,
            'priority': self.priority,
            'status': self.status,
            'notified': self.notified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Habit(db.Model):
    """Habit tracker model."""
    __tablename__ = 'habits'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    category = db.Column(db.String(50), default='Productivity')
    icon = db.Column(db.String(50), default='fa-check-circle')
    target_days_per_week = db.Column(db.Integer, default=7)
    current_streak = db.Column(db.Integer, default=0)
    best_streak = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    logs = db.relationship('HabitLog', backref='habit', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        today_str = date.today().isoformat()
        completed_today = any(log.date == today_str and log.completed for log in self.logs)
        
        # Calculate recent 7 days completion list
        past_7_days = []
        for i in range(6, -1, -1):
            d_str = (date.today() - timedelta(days=i)).isoformat()
            is_done = any(log.date == d_str and log.completed for log in self.logs)
            past_7_days.append({'date': d_str, 'completed': is_done})

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'icon': self.icon,
            'target_days_per_week': self.target_days_per_week,
            'current_streak': self.current_streak,
            'best_streak': self.best_streak,
            'completed_today': completed_today,
            'past_7_days': past_7_days,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class HabitLog(db.Model):
    """Daily record of completed habits."""
    __tablename__ = 'habit_logs'

    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)  # YYYY-MM-DD
    completed = db.Column(db.Boolean, default=True)
    notes = db.Column(db.String(255), default='')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'habit_id': self.habit_id,
            'date': self.date,
            'completed': self.completed,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class VoiceNote(db.Model):
    """Voice recordings and transcriptions."""
    __tablename__ = 'voice_notes'

    id = db.Column(db.Integer, primary_key=True)
    transcript = db.Column(db.Text, nullable=False)
    original_audio_path = db.Column(db.String(255), nullable=True)
    action_type = db.Column(db.String(50), default='Task Extraction')  # Task Extraction, Reminder, Note, Workout
    extracted_data = db.Column(db.Text, default='{}')  # JSON string
    status = db.Column(db.String(30), default='Processed')  # Recorded, Transcribing, Processed, Archived
    duration_seconds = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        try:
            parsed_data = json.loads(self.extracted_data) if self.extracted_data else {}
        except Exception:
            parsed_data = {}

        return {
            'id': self.id,
            'transcript': self.transcript,
            'original_audio_path': self.original_audio_path,
            'action_type': self.action_type,
            'extracted_data': parsed_data,
            'status': self.status,
            'duration_seconds': self.duration_seconds,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Conversation(db.Model):
    """AI Brain chat history."""
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    message = db.Column(db.Text, nullable=False)
    mode = db.Column(db.String(30), default='Demo AI')  # 'Local Ollama' or 'Demo AI'
    model_used = db.Column(db.String(50), default='llama3')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'message': self.message,
            'mode': self.mode,
            'model_used': self.model_used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Workout(db.Model):
    """Fitness and Gym tracking log."""
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), default='Strength')  # Strength, Cardio, Flexibility, HIIT
    sets = db.Column(db.Integer, default=3)
    reps = db.Column(db.Integer, default=10)
    weight = db.Column(db.Float, default=0.0)  # in kg
    duration_minutes = db.Column(db.Integer, default=30)
    calories_burned = db.Column(db.Integer, default=150)
    workout_date = db.Column(db.String(50), nullable=False)  # YYYY-MM-DD
    notes = db.Column(db.String(255), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'exercise_name': self.exercise_name,
            'category': self.category,
            'sets': self.sets,
            'reps': self.reps,
            'weight': self.weight,
            'duration_minutes': self.duration_minutes,
            'calories_burned': self.calories_burned,
            'workout_date': self.workout_date,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Device(db.Model):
    """ESP32 hardware status and telemetry."""
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100), default='ESP32-S3 Voice Node')
    device_type = db.Column(db.String(50), default='ESP32 Mic & LCD Terminal')
    ip_address = db.Column(db.String(50), default='192.168.1.150')
    status = db.Column(db.String(30), default='simulation')  # connected, simulation, offline
    wifi_ssid = db.Column(db.String(50), default='SecondBrain_Mesh_5G')
    battery_level = db.Column(db.Integer, default=92)       # percentage
    signal_strength = db.Column(db.Integer, default=-58)    # RSSI dBm
    temperature = db.Column(db.Float, default=38.4)         # Celsius
    mic_status = db.Column(db.String(30), default='Active / Ready')
    lcd_status = db.Column(db.String(30), default='Active (128x64 OLED)')
    lcd_text = db.Column(db.String(255), default='AI Second Brain: Ready')
    uptime_seconds = db.Column(db.Integer, default=14420)
    last_sync = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'ip_address': self.ip_address,
            'status': self.status,
            'wifi_ssid': self.wifi_ssid,
            'battery_level': self.battery_level,
            'signal_strength': self.signal_strength,
            'temperature': self.temperature,
            'mic_status': self.mic_status,
            'lcd_status': self.lcd_status,
            'lcd_text': self.lcd_text,
            'uptime_seconds': self.uptime_seconds,
            'last_sync': self.last_sync.strftime('%Y-%m-%d %H:%M:%S') if self.last_sync else None
        }


class Setting(db.Model):
    """Dynamic application settings."""
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255), default='')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


def seed_database(app):
    """Seed the database with rich demo data if empty."""
    with app.app_context():
        db.create_all()

        # Check if already seeded
        if Task.query.first():
            return

        today = date.today()
        today_str = today.isoformat()
        tomorrow_str = (today + timedelta(days=1)).isoformat()
        yesterday_str = (today - timedelta(days=1)).isoformat()

        # 1. User
        user = User(
            username='mausam_dev',
            email='mausam.cse@secondbrain.ai',
            full_name='Mausam Kumar',
            bio='B.Tech CSE Student | Building hardware-integrated AI agent systems.',
            avatar_url='https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=256&q=80'
        )
        db.session.add(user)

        # 2. Tasks
        sample_tasks = [
            Task(
                title='Complete B.Tech Minor Project Presentation',
                description='Prepare slides on ESP32 voice streaming and Whisper offline transcription integration.',
                category='College',
                priority='Urgent',
                due_date=today_str,
                completed=False
            ),
            Task(
                title='Submit Google Internship Application Form',
                description='Update resume with AI Second-Brain project highlights and submit portal link.',
                category='Internship',
                priority='High',
                due_date=tomorrow_str,
                completed=False
            ),
            Task(
                title='Optimize Local Ollama Prompt Template',
                description='Refactor system prompt to output structured JSON for task parsing.',
                category='Coding',
                priority='Medium',
                due_date=tomorrow_str,
                completed=True,
                completed_at=datetime.utcnow() - timedelta(hours=3)
            ),
            Task(
                title='Push ESP32 I2S Microphone Firmware to GitHub',
                description='Write unit test for audio buffer over Wi-Fi UDP stream.',
                category='GitHub',
                priority='High',
                due_date=(today + timedelta(days=2)).isoformat(),
                completed=False
            ),
            Task(
                title='Leg Day Workout: Squats & Romanian Deadlifts',
                description='Target: 4 sets x 8 reps at 90kg. Keep core tight.',
                category='Fitness',
                priority='Medium',
                due_date=today_str,
                completed=True,
                completed_at=datetime.utcnow() - timedelta(hours=5)
            ),
            Task(
                title='Buy 0.96 inch I2C OLED Display for ESP32',
                description='Order backup display modules from Robu.in or electronics store.',
                category='Personal',
                priority='Low',
                due_date=(today + timedelta(days=5)).isoformat(),
                completed=False
            )
        ]
        db.session.add_all(sample_tasks)

        # 3. Reminders
        sample_reminders = [
            Reminder(
                title='Internship Screening Call with Tech Recruiter',
                description='Review system design concepts and Second-Brain architecture details.',
                reminder_date=today_str,
                reminder_time='16:00',
                priority='Urgent',
                status='Today',
                notified=False
            ),
            Reminder(
                title='Submit Operating Systems Lab Assignment',
                description='Upload semaphore synchronization problem solutions on college portal.',
                reminder_date=tomorrow_str,
                reminder_time='11:30',
                priority='High',
                status='Upcoming',
                notified=False
            ),
            Reminder(
                title='Weekly GitHub Repo Maintenance & Tag Release',
                description='Draft v1.2.0 release notes with ESP32 LCD driver support.',
                reminder_date=(today + timedelta(days=3)).isoformat(),
                reminder_time='20:00',
                priority='Medium',
                status='Upcoming',
                notified=False
            ),
            Reminder(
                title='Drink Electrol / Hydration Water Target',
                description='Hit 3.5 liters daily target for workout recovery.',
                reminder_date=today_str,
                reminder_time='14:00',
                priority='Low',
                status='Completed',
                notified=True
            )
        ]
        db.session.add_all(sample_reminders)

        # 4. Habits
        habits_data = [
            ('Daily LeetCode Problem', 'Solve 1 Medium difficulty problem in Trees/Graphs', 'Coding', 'fa-code', 7, 14, 21),
            ('Gym Workout Session', '60 minutes strength training or cardio session', 'Fitness', 'fa-dumbbell', 6, 5, 18),
            ('Read Tech Research Paper', 'Read 5 pages of AI or embedded systems literature', 'College', 'fa-book-open', 5, 8, 12),
            ('Drink 3.5L Water', 'Stay hydrated throughout coding and college labs', 'Personal', 'fa-tint', 7, 24, 30),
            ('Git Commit Streak', 'Push meaningful commits or documentation to GitHub', 'GitHub', 'fa-code-branch', 7, 19, 45),
            ('10-Min Evening Meditation', 'Wind down and clear brain thoughts before sleep', 'Personal', 'fa-peace', 7, 4, 10)
        ]

        created_habits = []
        for name, desc, cat, icon, target, streak, best in habits_data:
            h = Habit(
                name=name,
                description=desc,
                category=cat,
                icon=icon,
                target_days_per_week=target,
                current_streak=streak,
                best_streak=best
            )
            created_habits.append(h)
            db.session.add(h)
        db.session.flush()

        # Seed habit logs for past 7 days
        for h in created_habits:
            for d in range(7):
                log_date = (today - timedelta(days=d)).isoformat()
                # Most days completed to show active streak
                is_done = True if d != 3 or h.category == 'Personal' else False
                log = HabitLog(
                    habit_id=h.id,
                    date=log_date,
                    completed=is_done,
                    notes='Completed on schedule via Second Brain trigger.' if is_done else 'Rest day'
                )
                db.session.add(log)

        # 5. Voice Notes
        sample_voice_notes = [
            VoiceNote(
                transcript='Remind me to complete my internship application tomorrow at 10 AM.',
                action_type='Reminder',
                extracted_data=json.dumps({
                    'title': 'Complete internship application',
                    'date': tomorrow_str,
                    'time': '10:00 AM',
                    'priority': 'High',
                    'category': 'Internship'
                }),
                status='Processed',
                duration_seconds=4
            ),
            VoiceNote(
                transcript='Add task finish the ESP32 audio streaming circuit diagram for minor project.',
                action_type='Task Extraction',
                extracted_data=json.dumps({
                    'title': 'Finish ESP32 audio streaming circuit diagram',
                    'date': today_str,
                    'time': 'End of day',
                    'priority': 'Urgent',
                    'category': 'College'
                }),
                status='Processed',
                duration_seconds=6
            ),
            VoiceNote(
                transcript='Log workout 4 sets bench press 80 kg 8 reps duration 45 minutes.',
                action_type='Workout',
                extracted_data=json.dumps({
                    'exercise': 'Bench Press',
                    'sets': 4,
                    'reps': 8,
                    'weight': 80,
                    'duration': 45,
                    'calories': 280
                }),
                status='Processed',
                duration_seconds=5
            )
        ]
        db.session.add_all(sample_voice_notes)

        # 6. Conversation history
        sample_convo = [
            Conversation(
                role='user',
                message='Hey Second Brain, give me a quick briefing of my high priority tasks and workout schedule today.',
                mode='Demo AI',
                model_used='llama3'
            ),
            Conversation(
                role='assistant',
                message="Good morning Mausam! Here is your Second-Brain tactical briefing:\n\n1. **Urgent Priority**: B.Tech Minor Project Presentation is due today.\n2. **High Priority**: Internship Screening Call at 4:00 PM.\n3. **Fitness**: Leg day workout completed (Squats 90kg logged, 380 kcal burned).\n4. **Hardware**: ESP32 Voice Node is connected with 92% battery and healthy Wi-Fi signal.\n\nWould you like me to rehearse your project elevator pitch or draft questions for your interview?",
                mode='Demo AI',
                model_used='llama3'
            )
        ]
        db.session.add_all(sample_convo)

        # 7. Workouts
        sample_workouts = [
            Workout(
                exercise_name='Barbell Back Squats',
                category='Strength',
                sets=4,
                reps=8,
                weight=90.0,
                duration_minutes=35,
                calories_burned=280,
                workout_date=today_str,
                notes='Solid form. Increased 5kg from last week.'
            ),
            Workout(
                exercise_name='Flat Dumbbell Bench Press',
                category='Strength',
                sets=4,
                reps=10,
                weight=32.5,
                duration_minutes=30,
                calories_burned=210,
                workout_date=yesterday_str,
                notes='Pushed hard on the last set. Great chest pump.'
            ),
            Workout(
                exercise_name='Pull-Ups & Lat Pulldown',
                category='Strength',
                sets=4,
                reps=12,
                weight=0.0,
                duration_minutes=25,
                calories_burned=180,
                workout_date=(today - timedelta(days=2)).isoformat(),
                notes='Full range of motion and 2s pause at top.'
            ),
            Workout(
                exercise_name='Incline Treadmill Sprints',
                category='Cardio',
                sets=6,
                reps=1,
                weight=0.0,
                duration_minutes=20,
                calories_burned=220,
                workout_date=(today - timedelta(days=3)).isoformat(),
                notes='High intensity interval training.'
            )
        ]
        db.session.add_all(sample_workouts)

        # 8. Device
        device = Device(
            device_name='ESP32-S3 Voice Node',
            device_type='ESP32 + I2S Mic + 0.96 OLED',
            ip_address='192.168.1.150',
            status='simulation',
            wifi_ssid='SecondBrain_Campus_5G',
            battery_level=92,
            signal_strength=-54,
            temperature=38.2,
            mic_status='Active / Listening',
            lcd_status='Online (I2C 0x3C)',
            lcd_text='AI Second Brain: Ready',
            uptime_seconds=18450
        )
        db.session.add(device)

        # 9. Settings
        initial_settings = [
            Setting(key='user_name', value='Mausam Kumar', description='User display name'),
            Setting(key='ai_model', value='llama3:8b', description='Selected Ollama model'),
            Setting(key='ollama_url', value='http://localhost:11434', description='Local Ollama server API endpoint'),
            Setting(key='whisper_mode', value='demo', description='Whisper transcription mode (local or demo)'),
            Setting(key='esp32_ip', value='192.168.1.150', description='ESP32 hardware IP address'),
            Setting(key='github_username', value='mausam-dev', description='GitHub username for portfolio sync'),
            Setting(key='demo_mode', value='true', description='Global demo and simulation mode flag'),
            Setting(key='notifications_enabled', value='true', description='Browser notifications enabled'),
            Setting(key='theme_mode', value='dark', description='Theme mode')
        ]
        db.session.add_all(initial_settings)

        db.session.commit()
