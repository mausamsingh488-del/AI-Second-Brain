# 🧠 AI Second-Brain — Personal Productivity & Edge Intelligence Node

> **"Your Second Brain. Always Listening. Always Thinking."**  
> An AI-powered personal productivity and memory assistant connected to an **ESP32-based hardware node** (with digital microphone & OLED display), local **Whisper STT** speech-to-text, and local **Ollama** LLM intelligence.

---

## 🎨 Theme & Color Palette

Designed with a modern cyber-organic dark glassmorphic palette:
- **`#D5851F` (Warm Ochre / Amber Gold)** — Primary interactive actions, urgent priority badges, AI sparks.
- **`#87A96B` (Asparagus / Cyber Sage Green)** — Success states, hardware alive signals, voice waveforms, streak flames.
- **`#5A3E2B` (Deep Bistre / Warm Brown)** — Structural panel warmth, depth, cyber dark undertones.
- **`#0F0D0B` / `#16120E` (Obsidian Base)** — Low eye-strain deep cyberpunk backdrop.

---

## 🚀 Key Features & Modules

1. **Mission Control Dashboard (`/dashboard`)**:
   - Live hardware status (Ollama, Whisper STT, ESP32 Node, SQLite DB).
   - 7 core KPI metrics: Tasks completed, pending, active habits, GitHub contributions, gym sessions, voice notes, AI memories.
   - 7-Day Chart.js productivity graphs & domain distribution doughnut.
   - Real-time today's action checklist with instant toggle.

2. **AI Neural Brain (`/brain`)**:
   - Conversational AI interface supporting **Ollama (Llama 3 / Mistral)** running locally.
   - **Zero-Crash Demo Fallback**: Returns intelligent context-aware responses if Ollama is not installed or running.
   - Chat history, copy response button, clear chat, and instant prompt chips.

3. **Voice Memory Assistant (`/voice`)**:
   - Browser MediaRecorder microphone capture with pulsing recording wave animation and timer.
   - Local Whisper STT integration + instant demo preset testing buttons.
   - **AI Entity Extraction Engine**: Parses speech into Task / Reminder / Workout with category, priority, date, and time.
   - One-click auto-save directly into the SQLite database.

4. **Smart Task Engine (`/tasks`)**:
   - Full CRUD task operations.
   - Categories: `College`, `Internship`, `Coding`, `Personal`, `Fitness`, `GitHub`.
   - Priorities: `Urgent`, `High`, `Medium`, `Low`.
   - Real-time search by keyword and multi-attribute filtering.

5. **Time-Sensitive Reminders (`/reminders`)**:
   - Auto-categorized tabs: `Today`, `Upcoming`, `Overdue`, `Completed`.
   - Native Browser Push Notifications with permission prompt and instant test alert.

6. **Habit Streak Tracker (`/habits`)**:
   - 7-day visual week history pills (click any day to toggle completion).
   - Streak counters (current active streak & personal best streak).
   - Habit completion rate analytics.

7. **GitHub Portfolio & Activity (`/github`)**:
   - 365-day contribution heatmap rendered with custom `#87A96B` and `#D5851F` levels.
   - Repository showcase cards with language badges, stars, and forks.
   - Live git commit activity stream.
   - Live GitHub API integration with seamless demo portfolio fallback.

8. **Fitness & Gym Progressive Overload (`/fitness`)**:
   - Log strength and cardio workouts (exercise name, sets, reps, weight kg, duration, calories).
   - Personal Records (PRs) tracker and weekly volume Chart.js graph.

9. **ESP32 Hardware Node Console (`/device`)**:
   - Realistic virtual PCB board schematic with live 0.96" OLED screen.
   - Live telemetry: Battery %, Wi-Fi RSSI, SoC Temperature, Device Uptime.
   - Interactive Hardware Test Bench: "Test Digital Microphone", "Push Text to OLED", "Sync Time", "Restart Node", "Toggle Connection".
   - Serial UART terminal communication log stream.

10. **System Preferences & Configuration (`/settings`)**:
    - Configure display name, GitHub username, Ollama URL, Whisper mode, ESP32 IP, and Demo mode flag.
    - **One-Click Demo Database Reset**: Re-seed database with realistic sample data anytime for presentations.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3 (Glassmorphism, custom cyber variables), Vanilla JavaScript (no npm/Node.js build step needed!), Bootstrap 5, Font Awesome 6, Chart.js.
- **Backend**: Python 3.10+, Flask 3, Jinja2 Templates.
- **Database**: SQLite with Flask-SQLAlchemy ORM (Zero configuration; auto-created on first run).
- **AI / Speech**: Local Ollama LLM HTTP API, Whisper Speech-to-Text, Browser MediaRecorder API.
- **Hardware Integration**: ESP32-S3 Wi-Fi micro-server with simulated fallback.

---

## 📦 Quick Start Guide (Beginner Friendly)

### Step 1: Extract the Project ZIP
Extract the downloaded `AI-Second-Brain.zip` to a folder on your computer.

### Step 2: Open in VS Code
Open Visual Studio Code, click **File > Open Folder...**, and select the extracted `AI-Second-Brain` folder.

### Step 3: Open the Terminal in VS Code
Press `` Ctrl + ` `` (or click **Terminal > New Terminal**).

---

### Step 4: Setup Python Virtual Environment

#### On Windows (PowerShell or CMD):
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate
```
*(If PowerShell blocks script execution, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` once).*

#### On macOS / Linux:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

---

### Step 5: Install Requirements
Run:
```bash
pip install -r requirements.txt
```
*(This installs Flask, Flask-SQLAlchemy, requests, and python-dotenv. No heavy C++ compilers or GPU libraries required).*

---

### Step 6: (Optional) Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```
*(By default, `DEMO_MODE=true` is enabled, allowing everything to work immediately without any external hardware).*

---

### Step 7: Launch the Application
Run:
```bash
python app.py
```

You should see output similar to:
```
=======================================================
  🧠 AI Second-Brain Dashboard starting...
  ⚡ Running on http://127.0.0.1:5000
  🎯 Mode: DEMO / SIMULATION (Full local test)
  Hardware: ESP32 Emulated Node (192.168.1.150)
=======================================================
```

### Step 8: Open in Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
- Visit `http://127.0.0.1:5000/` for the Futuristic Landing Page.
- Visit `http://127.0.0.1:5000/dashboard` for the Control Panel.

---

## 🔌 Connecting Real Hardware & Local AI (Optional)

### 1. Connecting Local Ollama (Free & Private)
1. Download Ollama from [https://ollama.com](https://ollama.com).
2. Open terminal and run:
   ```bash
   ollama run llama3
   ```
3. The dashboard will automatically detect Ollama at `http://localhost:11434` and switch the AI Brain mode from **"Demo Mode"** to **"Local Ollama"**!

### 2. Connecting Local Whisper STT (Optional)
If you have Python and FFmpeg installed, you can optionally install OpenAI Whisper:
```bash
pip install openai-whisper
```
When installed, real voice recordings are transcribed locally. If omitted, the application uses built-in smart demo transcription seamlessly.

### 3. Connecting Real ESP32 Hardware
Wiring diagram for ESP32-S3:
- **I2S Microphone (INMP441)**:
  - `SCK` ➔ `GPIO 14`
  - `WS`  ➔ `GPIO 15`
  - `SD`  ➔ `GPIO 32`
  - `VDD` ➔ `3.3V`, `GND` ➔ `GND`
- **0.96" OLED Display (SSD1306 I2C)**:
  - `SDA` ➔ `GPIO 21`
  - `SCL` ➔ `GPIO 22`
  - `VCC` ➔ `3.3V`, `GND` ➔ `GND`

In `/settings`, set the **ESP32 IP Address** to your device's local LAN IP.

---

## 🎯 College Presentation / Viva Checklist

When presenting this project for a B.Tech CSE presentation:
1. **Explain the Architecture**:
   `ESP32 Hardware Node ➔ Whisper STT ➔ Local Ollama LLM ➔ Flask REST API ➔ SQLite DB ➔ Realtime UI Dashboard`.
2. **Show Offline Privacy**: Highlight that all AI inference and voice processing happen on the edge without sending data to third-party Big Tech cloud APIs.
3. **Voice to Action Demonstration**:
   - Go to `/voice`
   - Click one of the instant presets (e.g., *"Remind me to complete my internship application tomorrow at 10 AM"*).
   - Show how the entity extractor parses the date, time, and priority into a structured card and inserts it into `/reminders` or `/tasks`.
4. **Hardware Simulation**: Show the `/device` tab to demonstrate live OLED buffer updates, microphone acoustic loopback tests, and telemetry dials.
5. **Resetting for Clean Viva**: If you need to reset the data back to fresh demo state, go to `/settings` and click **"Reset & Re-Seed SQLite DB"**.

---

## 📁 Project Structure

```
AI-Second-Brain/
│
├── app.py                      # Flask App Factory, Error Handlers, and Seed Trigger
├── config.py                   # Central Configuration & Environment Settings
├── requirements.txt            # Minimal dependencies
├── README.md                   # Complete Documentation
├── .env.example                # Environment Variable Template
├── .gitignore                  # Git Ignore rules
│
├── database/
│   └── second_brain.db         # SQLite Database (auto-generated)
│
├── models/
│   └── models.py               # SQLAlchemy Models: User, Task, Reminder, Habit, Workout, Device
│
├── routes/
│   ├── main.py                 # Frontend Views (Landing, Dashboard, Brain, Voice, etc.)
│   ├── api.py                  # Stats, Chart Analytics, Settings endpoints
│   ├── tasks.py                # Smart Tasks & Reminders CRUD APIs
│   ├── habits.py               # Habits & Fitness Workout APIs
│   └── voice.py                # Voice Transcription, AI Chat, and Hardware APIs
│
├── services/
│   ├── whisper_service.py      # Whisper Speech-to-Text & Entity Extractor
│   ├── ollama_service.py       # Local Ollama AI & Demo Intelligence Engine
│   ├── esp32_service.py        # ESP32 Communication & Hardware Simulator
│   └── github_service.py       # GitHub API integration & 365-day Heatmap Generator
│
├── templates/
│   ├── base.html               # Cyber Base Layout with Topbar & Sidebar
│   ├── index.html              # Landing Page with Flowchart Architecture
│   ├── dashboard.html          # Mission Control Dashboard
│   ├── brain.html              # AI Neural Brain Chat
│   ├── voice.html              # Voice Assistant & Dictation Console
│   ├── tasks.html              # Smart Tasks Manager
│   ├── reminders.html          # Time-Sensitive Reminders
│   ├── habits.html             # Habit Tracker & Streaks
│   ├── github.html             # GitHub Portfolio & 365 Heatmap
│   ├── fitness.html            # Gym & Progressive Overload Tracker
│   ├── analytics.html          # Deep Analytics & Velocity Charts
│   ├── device.html             # ESP32 Hardware Monitor & Terminal
│   ├── settings.html           # Settings & SQLite Re-Seeder
│   └── 404.html                # 404 Error Page
│
├── static/
│   ├── css/
│   │   └── style.css           # Custom #87A96B, #5A3E2B, #D5851F Design System
│   └── js/
│       ├── main.js             # Global Utilities & Clock
│       ├── dashboard.js        # KPI & Chart.js Controllers
│       ├── voice.js            # MediaRecorder & Voice Audio Controller
│       ├── tasks.js            # Task Filtering & CRUD Controller
│       ├── habits.js           # Habit Streaks Controller
│       ├── github.js           # GitHub Heatmap & Stream Controller
│       ├── fitness.js          # Workout Log & Calories Controller
│       └── device.js           # ESP32 Hardware & OLED Controller
│
└── uploads/                    # Temporary audio uploads folder
```

---

## 🛡️ License

Built for educational, research, and personal productivity use.
Enjoy your AI Second-Brain! 🚀
