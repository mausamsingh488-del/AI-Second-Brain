import os
from datetime import datetime, date
from flask import Flask, render_template, jsonify
from config import Config
from models.models import db, seed_database


def create_app(config_class=Config):
    """Application factory for AI Second-Brain."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    from routes.main import main_bp
    from routes.api import api_bp
    from routes.tasks import tasks_bp
    from routes.habits import habits_bp
    from routes.voice import voice_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(habits_bp)
    app.register_blueprint(voice_bp)

    # Inject global context into all templates
    @app.context_processor
    def inject_globals():
        return {
            'app_name': 'AI Second-Brain',
            'demo_mode': app.config.get('DEMO_MODE', True),
            'current_year': datetime.now().year,
            'today_date': date.today().strftime('%A, %B %d, %Y'),
            'theme_colors': app.config.get('THEME_COLORS', {})
        }

    # Custom Error Handlers (Beginner friendly & never expose raw tracebacks)
    @app.errorhandler(404)
    def page_not_found(e):
        if app.request_class:
            from flask import request
            if request.path.startswith('/api/'):
                return jsonify({"status": "error", "message": "API endpoint not found"}), 404
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        if app.request_class:
            from flask import request
            if request.path.startswith('/api/'):
                return jsonify({"status": "error", "message": "Internal server error. Demo mode active."}), 500
        return render_template('404.html', error_title="System Anomaly", error_msg="The Second-Brain encountered an unexpected condition. Operating in safe demo mode."), 500

    # Initialize and seed database automatically
    with app.app_context():
        seed_database(app)

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n=======================================================")
    print("  [*] AI Second-Brain Dashboard starting...")
    print(f"  [+] Running on http://127.0.0.1:{port}")
    print(f"  [>] Mode: {'DEMO / SIMULATION (Full local test)' if app.config['DEMO_MODE'] else 'PRODUCTION'}")
    print(f"  [#] Hardware: ESP32 Emulated Node ({app.config['ESP32_IP']})")
    print("=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=False)

