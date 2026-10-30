from flask import Blueprint, jsonify, request
from datetime import datetime, date, timedelta
from models.models import db, Habit, HabitLog, Workout

habits_bp = Blueprint('habits', __name__, url_prefix='/api')


# ==================== HABITS API ====================

@habits_bp.route('/habits', methods=['GET'])
def get_habits():
    """Get all habits with computed streaks and today's status."""
    try:
        habits = Habit.query.order_by(Habit.id.asc()).all()
        return jsonify({
            "status": "success",
            "count": len(habits),
            "habits": [h.to_dict() for h in habits]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@habits_bp.route('/habits', methods=['POST'])
def create_habit():
    """Create a new habit."""
    try:
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        if not name:
            return jsonify({"status": "error", "message": "Habit name is required"}), 400

        habit = Habit(
            name=name,
            description=data.get('description', '').strip(),
            category=data.get('category', 'Productivity'),
            icon=data.get('icon', 'fa-check-circle'),
            target_days_per_week=int(data.get('target_days_per_week', 7)),
            current_streak=0,
            best_streak=0
        )
        db.session.add(habit)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Habit created successfully",
            "habit": habit.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@habits_bp.route('/habits/<int:habit_id>/toggle', methods=['POST'])
def toggle_habit_today(habit_id):
    """Toggle today's completion for a habit and recalculate streak."""
    try:
        data = request.get_json() or {}
        target_date_str = data.get('date') or date.today().isoformat()

        habit = Habit.query.get_or_404(habit_id)
        log = HabitLog.query.filter_by(habit_id=habit.id, date=target_date_str).first()

        if log:
            log.completed = not log.completed
        else:
            log = HabitLog(
                habit_id=habit.id,
                date=target_date_str,
                completed=True,
                notes='Logged via dashboard'
            )
            db.session.add(log)

        # Recalculate streak
        all_logs = {l.date: l.completed for l in habit.logs}
        all_logs[target_date_str] = log.completed

        streak = 0
        curr = date.today()
        while True:
            d_str = curr.isoformat()
            if all_logs.get(d_str, False):
                streak += 1
                curr -= timedelta(days=1)
            else:
                # If today is not completed yet, streak might continue from yesterday
                if curr == date.today() and not all_logs.get(d_str, False):
                    curr -= timedelta(days=1)
                    continue
                break

        habit.current_streak = streak
        if streak > habit.best_streak:
            habit.best_streak = streak

        db.session.commit()
        return jsonify({
            "status": "success",
            "completed": log.completed,
            "habit": habit.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@habits_bp.route('/habits/<int:habit_id>', methods=['DELETE'])
def delete_habit(habit_id):
    """Delete a habit."""
    try:
        habit = Habit.query.get_or_404(habit_id)
        db.session.delete(habit)
        db.session.commit()
        return jsonify({"status": "success", "message": "Habit deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


# ==================== FITNESS / WORKOUT API ====================

@habits_bp.route('/fitness', methods=['GET'])
def get_fitness():
    """Get all workouts and fitness summary stats."""
    try:
        workouts = Workout.query.order_by(Workout.workout_date.desc(), Workout.id.desc()).all()
        
        # Summary statistics
        total_calories = sum(w.calories_burned for w in workouts)
        total_minutes = sum(w.duration_minutes for w in workouts)
        
        # Weekly workouts
        week_ago_str = (date.today() - timedelta(days=7)).isoformat()
        weekly_count = Workout.query.filter(Workout.workout_date >= week_ago_str).count()

        return jsonify({
            "status": "success",
            "stats": {
                "total_workouts": len(workouts),
                "weekly_workouts": weekly_count,
                "total_calories": total_calories,
                "total_duration_minutes": total_minutes,
                "active_streak": 5
            },
            "workouts": [w.to_dict() for w in workouts]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@habits_bp.route('/fitness', methods=['POST'])
def log_workout():
    """Log a new workout session."""
    try:
        data = request.get_json() or {}
        exercise_name = data.get('exercise_name', '').strip()
        if not exercise_name:
            return jsonify({"status": "error", "message": "Exercise name is required"}), 400

        workout = Workout(
            exercise_name=exercise_name,
            category=data.get('category', 'Strength'),
            sets=int(data.get('sets', 3)),
            reps=int(data.get('reps', 10)),
            weight=float(data.get('weight', 0.0)),
            duration_minutes=int(data.get('duration_minutes', 30)),
            calories_burned=int(data.get('calories_burned', 150)),
            workout_date=data.get('workout_date') or date.today().isoformat(),
            notes=data.get('notes', '').strip()
        )
        db.session.add(workout)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Workout session logged successfully",
            "workout": workout.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@habits_bp.route('/fitness/<int:workout_id>', methods=['DELETE'])
def delete_workout(workout_id):
    """Delete a workout log."""
    try:
        workout = Workout.query.get_or_404(workout_id)
        db.session.delete(workout)
        db.session.commit()
        return jsonify({"status": "success", "message": "Workout record deleted"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
