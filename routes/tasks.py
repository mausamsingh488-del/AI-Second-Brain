from flask import Blueprint, jsonify, request
from datetime import datetime, date
from models.models import db, Task, Reminder

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api')


# ==================== TASKS API ====================

@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """Retrieve tasks with optional category, priority, status and search filtering."""
    try:
        query = Task.query

        # Filters
        category = request.args.get('category')
        if category and category != 'All':
            query = query.filter_by(category=category)

        priority = request.args.get('priority')
        if priority and priority != 'All':
            query = query.filter_by(priority=priority)

        status = request.args.get('status')
        if status == 'completed':
            query = query.filter_by(completed=True)
        elif status == 'pending':
            query = query.filter_by(completed=False)

        search = request.args.get('q')
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(Task.title.ilike(search_pattern) | Task.description.ilike(search_pattern))

        # Order by completed ascending, then created_at descending
        tasks_list = query.order_by(Task.completed.asc(), Task.id.desc()).all()
        return jsonify({
            "status": "success",
            "count": len(tasks_list),
            "tasks": [t.to_dict() for t in tasks_list]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@tasks_bp.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task."""
    try:
        data = request.get_json() or {}
        title = data.get('title', '').strip()
        if not title:
            return jsonify({"status": "error", "message": "Task title is required"}), 400

        task = Task(
            title=title,
            description=data.get('description', '').strip(),
            category=data.get('category', 'Personal'),
            priority=data.get('priority', 'Medium'),
            due_date=data.get('due_date') or date.today().isoformat(),
            completed=False
        )
        db.session.add(task)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Task created successfully",
            "task": task.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@tasks_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get single task details."""
    task = Task.query.get_or_404(task_id)
    return jsonify({"status": "success", "task": task.to_dict()})


@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update task details."""
    try:
        task = Task.query.get_or_404(task_id)
        data = request.get_json() or {}

        if 'title' in data:
            task.title = data['title'].strip()
        if 'description' in data:
            task.description = data['description'].strip()
        if 'category' in data:
            task.category = data['category']
        if 'priority' in data:
            task.priority = data['priority']
        if 'due_date' in data:
            task.due_date = data['due_date']
        if 'completed' in data:
            task.completed = bool(data['completed'])
            task.completed_at = datetime.utcnow() if task.completed else None

        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Task updated successfully",
            "task": task.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@tasks_bp.route('/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    """Toggle task completion status."""
    try:
        task = Task.query.get_or_404(task_id)
        task.completed = not task.completed
        task.completed_at = datetime.utcnow() if task.completed else None
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"Task marked as {'completed' if task.completed else 'pending'}",
            "task": task.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task."""
    try:
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return jsonify({"status": "success", "message": "Task deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


# ==================== REMINDERS API ====================

@tasks_bp.route('/reminders', methods=['GET'])
def get_reminders():
    """Retrieve reminders with dynamic status updating (Today, Upcoming, Completed, Overdue)."""
    try:
        today_str = date.today().isoformat()
        reminders = Reminder.query.order_by(Reminder.reminder_date.asc(), Reminder.reminder_time.asc()).all()

        # Dynamic status refresh
        for r in reminders:
            if r.status != 'Completed':
                if r.reminder_date == today_str:
                    r.status = 'Today'
                elif r.reminder_date < today_str:
                    r.status = 'Overdue'
                else:
                    r.status = 'Upcoming'
        db.session.commit()

        status_filter = request.args.get('status')
        if status_filter and status_filter != 'All':
            filtered = [r for r in reminders if r.status.lower() == status_filter.lower()]
        else:
            filtered = reminders

        return jsonify({
            "status": "success",
            "count": len(filtered),
            "reminders": [r.to_dict() for r in filtered]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@tasks_bp.route('/reminders', methods=['POST'])
def create_reminder():
    """Create a new reminder."""
    try:
        data = request.get_json() or {}
        title = data.get('title', '').strip()
        if not title:
            return jsonify({"status": "error", "message": "Reminder title is required"}), 400

        rem_date = data.get('reminder_date') or date.today().isoformat()
        today_str = date.today().isoformat()
        status = 'Today' if rem_date == today_str else ('Upcoming' if rem_date > today_str else 'Overdue')

        reminder = Reminder(
            title=title,
            description=data.get('description', '').strip(),
            reminder_date=rem_date,
            reminder_time=data.get('reminder_time', '10:00'),
            priority=data.get('priority', 'Medium'),
            status=status,
            notified=False
        )
        db.session.add(reminder)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Reminder created successfully",
            "reminder": reminder.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@tasks_bp.route('/reminders/<int:reminder_id>/toggle', methods=['POST'])
def toggle_reminder(reminder_id):
    """Toggle reminder between Completed and Active status."""
    try:
        reminder = Reminder.query.get_or_404(reminder_id)
        today_str = date.today().isoformat()

        if reminder.status == 'Completed':
            if reminder.reminder_date == today_str:
                reminder.status = 'Today'
            elif reminder.reminder_date < today_str:
                reminder.status = 'Overdue'
            else:
                reminder.status = 'Upcoming'
        else:
            reminder.status = 'Completed'

        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"Reminder status set to {reminder.status}",
            "reminder": reminder.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@tasks_bp.route('/reminders/<int:reminder_id>', methods=['DELETE'])
def delete_reminder(reminder_id):
    """Delete a reminder."""
    try:
        reminder = Reminder.query.get_or_404(reminder_id)
        db.session.delete(reminder)
        db.session.commit()
        return jsonify({"status": "success", "message": "Reminder deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
