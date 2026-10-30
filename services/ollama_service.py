import requests
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class OllamaService:
    """Service to interact with local Ollama server, with intelligent demo fallback."""

    def __init__(self, base_url="http://localhost:11434", default_model="llama3"):
        self.base_url = base_url.rstrip('/')
        self.default_model = default_model

    def is_available(self) -> bool:
        """Check if local Ollama server is responsive."""
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=1.5)
            return res.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list:
        """Fetch available models from Ollama."""
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=2.0)
            if res.status_code == 200:
                data = res.json()
                return [m.get('name') for m in data.get('models', [])]
        except Exception:
            pass
        return ['llama3:8b (Local Simulated)', 'mistral:7b', 'phi3:mini', 'neural-chat']

    def generate_chat_response(self, prompt: str, conversation_history: list = None, model: str = None) -> dict:
        """Generate AI response using Ollama if running, otherwise use intelligent Demo AI."""
        chosen_model = model or self.default_model
        
        # Check if real Ollama is active
        if self.is_available():
            try:
                # Build messages array for Ollama Chat API
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are the AI Second-Brain Assistant, an intelligent, concise, and helpful personal "
                            "productivity AI running on an edge device (ESP32 node with local LLM). You help the user "
                            "manage tasks, reminders, college academic deadlines, coding projects, GitHub repos, and fitness tracking."
                        )
                    }
                ]
                if conversation_history:
                    for item in conversation_history[-6:]:
                        messages.append({"role": item.get('role', 'user'), "content": item.get('message', '')})

                messages.append({"role": "user", "content": prompt})

                payload = {
                    "model": chosen_model,
                    "messages": messages,
                    "stream": False
                }
                res = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=25.0)
                if res.status_code == 200:
                    resp_data = res.json()
                    bot_text = resp_data.get('message', {}).get('content', '')
                    return {
                        "text": bot_text,
                        "mode": "Local Ollama",
                        "model": chosen_model,
                        "status": "success",
                        "is_demo": False
                    }
            except Exception as e:
                logger.warning(f"Ollama call failed, falling back to Demo AI: {e}")

        # Intelligent Demo Fallback
        demo_reply = self._generate_intelligent_demo_response(prompt)
        return {
            "text": demo_reply,
            "mode": "Demo AI Mode",
            "model": f"{chosen_model} (Simulated)",
            "status": "demo_active",
            "is_demo": True
        }

    def _generate_intelligent_demo_response(self, prompt: str) -> str:
        """Generate high-quality context-aware demo responses for college / productivity queries."""
        p_lower = prompt.lower()

        if any(w in p_lower for w in ['task', 'priority', 'schedule', 'todo', 'today']):
            return (
                "🎯 **Here is your Today's Second-Brain Briefing:**\n\n"
                "• **Urgent Task**: Complete B.Tech Minor Project Presentation (Due Today)\n"
                "• **High Priority**: Google Internship Application submission (Due Tomorrow)\n"
                "• **Today's Reminder**: Interview screening call at 4:00 PM\n"
                "• **Completed**: Leg Day Workout (Squats 90kg logged)\n\n"
                "💡 *Suggestion*: Allocate a 90-minute deep work block now to finalize your project slides before the 4 PM screening call."
            )

        if any(w in p_lower for w in ['esp32', 'hardware', 'device', 'mic', 'lcd']):
            return (
                "⚡ **ESP32 Hardware Node Status:**\n\n"
                "• **Device Model**: ESP32-S3 Dual-Core Xtensa LX7\n"
                "• **Connection**: Wi-Fi Mesh Connected (`192.168.1.150`)\n"
                "• **Microphone**: I2S INMP441 Omnidirectional Mic — Active / 16kHz audio stream\n"
                "• **Display**: 0.96\" SSD1306 OLED (128x64) — Status: 'AI Second Brain: Ready'\n"
                "• **Battery**: 92% | Temperature: 38.2°C | Uptime: 5h 12m\n\n"
                "All audio packets are securely buffered and processed locally via Whisper STT."
            )

        if any(w in p_lower for w in ['github', 'commit', 'repo', 'code', 'git']):
            return (
                "💻 **GitHub Activity & Code Summary:**\n\n"
                "• **Active Streak**: 19 consecutive days with commits\n"
                "• **Total Public Repos**: 24 repositories\n"
                "• **Latest Repo**: `esp32-voice-second-brain` (Python / C++)\n"
                "• **Pending PR**: `#14 - Fix I2S DMA audio buffer underflow on ESP32-S3`\n\n"
                "Your contribution heatmap shows peak activity on Tuesday and Thursday evenings!"
            )

        if any(w in p_lower for w in ['gym', 'workout', 'fitness', 'exercise', 'calories']):
            return (
                "💪 **Fitness & Gym Telemetry:**\n\n"
                "• **Weekly Streak**: 5 active workout days this week\n"
                "• **Today's Log**: Barbell Back Squats — 4 sets × 8 reps @ 90kg\n"
                "• **Calories Burned Today**: ~490 kcal\n"
                "• **Weekly Workout Time**: 2h 45m\n\n"
                "You are on track to hit your weekly target of 6 sessions. Remember to maintain proper hydration (3.5L target)!"
            )

        if any(w in p_lower for w in ['habit', 'streak', 'water', 'meditation']):
            return (
                "🔥 **Habit Performance Matrix:**\n\n"
                "• **Daily LeetCode Problem**: 14-day streak ⭐\n"
                "• **3.5L Water Intake**: 24-day streak (Completed today)\n"
                "• **Read Tech Research Paper**: 8-day streak\n"
                "• **Current Overall Consistency**: 88% completion rate this month.\n\n"
                "Keep going! Completing your meditation tonight will extend your streak to 5 days."
            )

        if any(w in p_lower for w in ['who are you', 'what are you', 'help', 'introduce']):
            return (
                "🧠 **I am your AI Second-Brain Assistant!**\n\n"
                "I am a personal memory and productivity system designed to integrate with your physical workspace via an **ESP32 hardware terminal** equipped with a microphone and OLED display.\n\n"
                "**What I can do:**\n"
                "1. **Voice Input**: Capture spontaneous thoughts via browser mic or ESP32 hardware.\n"
                "2. **Smart Task & Reminder Engine**: Categorize assignments, internships, and deadlines.\n"
                "3. **Local AI Privacy**: Run locally using Ollama and Whisper without sending your data to third-party clouds.\n"
                "4. **Developer & Fitness Tracking**: Monitor your GitHub activity and gym progressive overload."
            )

        # Default helpful synthesis
        return (
            f"🧠 **AI Second-Brain Analysis:**\n\n"
            f"I have processed your inquiry: *\"{prompt}\"*.\n\n"
            f"Here are key insights from your second brain's memory bank:\n"
            f"• **Context**: You are currently balancing B.Tech CSE coursework with internship preparation and physical training.\n"
            f"• **Recommendation**: Break your objective into a 3-step action item and register it into your Smart Tasks tab.\n"
            f"• **System Note**: Operating in Demo AI Mode. Real local inference can be enabled anytime by launching `ollama run llama3`."
        )


ollama_service = OllamaService()
