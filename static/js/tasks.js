// ==========================================================================
// AI SECOND-BRAIN: TASKS MANAGEMENT CONTROLLER
// Handles filtering, searching, CRUD, and modals for tasks.
// ==========================================================================

let currentStatusFilter = 'all';
let allLoadedTasks = [];

document.addEventListener('DOMContentLoaded', () => {
  // Set default due date to today in add modal
  const todayStr = new Date().toISOString().split('T')[0];
  const dateInput = document.getElementById('newTaskDueDate');
  if (dateInput) dateInput.value = todayStr;

  fetchTasks();
});

async function fetchTasks() {
  const container = document.getElementById('tasksCardsContainer');
  try {
    const res = await fetch('/api/tasks');
    const data = await res.json();
    if (data.status !== 'success') throw new Error(data.message);

    allLoadedTasks = data.tasks || [];
    updateTabCounts();
    renderFilteredTasks();
  } catch (err) {
    container.innerHTML = `<div class="col-12 text-center text-danger py-4">Error loading tasks: ${err.message}</div>`;
  }
}

function updateTabCounts() {
  const allCount = allLoadedTasks.length;
  const pendingCount = allLoadedTasks.filter(t => !t.completed).length;
  const completedCount = allLoadedTasks.filter(t => t.completed).length;

  document.getElementById('countAll').textContent = allCount;
  document.getElementById('countPending').textContent = pendingCount;
  document.getElementById('countCompleted').textContent = completedCount;
}

function setStatusTab(status) {
  currentStatusFilter = status;

  ['tabAll', 'tabPending', 'tabCompleted'].forEach(id => {
    document.getElementById(id).className = 'btn btn-sm btn-dark text-muted';
  });

  if (status === 'all') {
    document.getElementById('tabAll').className = 'btn btn-sm btn-outline-brain';
  } else if (status === 'pending') {
    document.getElementById('tabPending').className = 'btn btn-sm btn-outline-brain';
  } else {
    document.getElementById('tabCompleted').className = 'btn btn-sm btn-outline-brain';
  }

  renderFilteredTasks();
}

function filterTasks() {
  renderFilteredTasks();
}

function renderFilteredTasks() {
  const container = document.getElementById('tasksCardsContainer');
  const search = (document.getElementById('taskSearchInput').value || '').toLowerCase().trim();
  const category = document.getElementById('taskCategoryFilter').value;
  const priority = document.getElementById('taskPriorityFilter').value;

  let filtered = allLoadedTasks;

  // Status
  if (currentStatusFilter === 'pending') {
    filtered = filtered.filter(t => !t.completed);
  } else if (currentStatusFilter === 'completed') {
    filtered = filtered.filter(t => t.completed);
  }

  // Category
  if (category !== 'All') {
    filtered = filtered.filter(t => t.category.toLowerCase() === category.toLowerCase());
  }

  // Priority
  if (priority !== 'All') {
    filtered = filtered.filter(t => t.priority.toLowerCase() === priority.toLowerCase());
  }

  // Search
  if (search) {
    filtered = filtered.filter(t => 
      t.title.toLowerCase().includes(search) || 
      (t.description && t.description.toLowerCase().includes(search))
    );
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="col-12 text-center py-5 text-muted">
        <i class="fa-solid fa-list-check mb-2" style="font-size: 2rem; color: var(--color-dark-acc);"></i>
        <div class="fw-semibold">No tasks match your criteria</div>
        <small>Try clearing filters or add a new task!</small>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(t => `
    <div class="col-lg-6 col-12">
      <div class="glass-panel p-3 h-100 position-relative ${t.completed ? 'opacity-75' : ''}" style="background: rgba(32, 24, 18, 0.75);">
        <div class="d-flex align-items-start justify-content-between gap-3">
          <div class="d-flex align-items-start gap-3 flex-grow-1">
            <input type="checkbox" class="form-check-input mt-1" style="width: 22px; height: 22px; cursor: pointer; accent-color: var(--color-primary);" ${t.completed ? 'checked' : ''} onchange="toggleTaskItem(${t.id})">
            <div>
              <h6 class="fw-bold mb-1 ${t.completed ? 'text-decoration-line-through text-muted' : 'text-white'}" style="font-size: 0.95rem;">
                ${escapeHtml(t.title)}
              </h6>
              ${t.description ? `<p class="text-muted mb-2" style="font-size: 0.82rem; line-height: 1.4;">${escapeHtml(t.description)}</p>` : ''}
              
              <div class="d-flex flex-wrap align-items-center gap-2 mt-2">
                <span class="badge" style="background: rgba(90, 62, 43, 0.5); color: #ffca7b; font-size: 0.72rem;">
                  <i class="fa-solid fa-tag me-1"></i>${t.category}
                </span>
                <span class="badge badge-priority-${t.priority.toLowerCase()}" style="font-size: 0.72rem;">
                  ${t.priority}
                </span>
                <span class="text-muted font-mono" style="font-size: 0.75rem;">
                  <i class="fa-regular fa-calendar me-1"></i>${t.due_date || 'No due date'}
                </span>
              </div>
            </div>
          </div>

          <!-- Actions menu -->
          <div class="d-flex align-items-center gap-1">
            <button class="btn btn-sm btn-dark text-muted" title="Edit task" onclick="openEditTaskModal(${t.id})">
              <i class="fa-solid fa-pen" style="font-size: 0.75rem;"></i>
            </button>
            <button class="btn btn-sm btn-dark text-danger" title="Delete task" onclick="deleteTaskItem(${t.id})">
              <i class="fa-solid fa-trash-can" style="font-size: 0.75rem;"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  `).join('');
}

async function handleCreateTask(e) {
  e.preventDefault();
  const payload = {
    title: document.getElementById('newTaskTitle').value.trim(),
    description: document.getElementById('newTaskDesc').value.trim(),
    category: document.getElementById('newTaskCategory').value,
    priority: document.getElementById('newTaskPriority').value,
    due_date: document.getElementById('newTaskDueDate').value
  };

  try {
    const res = await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.status === 'success') {
      showToast('Task added to Second Brain!', 'success');
      document.getElementById('createTaskForm').reset();
      bootstrap.Modal.getInstance(document.getElementById('addTaskModal')).hide();
      fetchTasks();
    } else {
      showToast(data.message, 'error');
    }
  } catch (err) {
    showToast('Failed to create task', 'error');
  }
}

function openEditTaskModal(id) {
  const task = allLoadedTasks.find(t => t.id === id);
  if (!task) return;

  document.getElementById('editTaskId').value = task.id;
  document.getElementById('editTaskTitle').value = task.title;
  document.getElementById('editTaskDesc').value = task.description || '';
  document.getElementById('editTaskCategory').value = task.category;
  document.getElementById('editTaskPriority').value = task.priority;
  document.getElementById('editTaskDueDate').value = task.due_date || '';

  const modal = new bootstrap.Modal(document.getElementById('editTaskModal'));
  modal.show();
}

async function handleEditTask(e) {
  e.preventDefault();
  const id = document.getElementById('editTaskId').value;
  const payload = {
    title: document.getElementById('editTaskTitle').value.trim(),
    description: document.getElementById('editTaskDesc').value.trim(),
    category: document.getElementById('editTaskCategory').value,
    priority: document.getElementById('editTaskPriority').value,
    due_date: document.getElementById('editTaskDueDate').value
  };

  try {
    const res = await fetch(`/api/tasks/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.status === 'success') {
      showToast('Task updated!', 'success');
      bootstrap.Modal.getInstance(document.getElementById('editTaskModal')).hide();
      fetchTasks();
    }
  } catch (err) {
    showToast('Failed to update task', 'error');
  }
}

async function toggleTaskItem(id) {
  try {
    const res = await fetch(`/api/tasks/${id}/toggle`, { method: 'POST' });
    const data = await res.json();
    if (data.status === 'success') {
      showToast(data.message, 'success');
      fetchTasks();
    }
  } catch (err) {
    showToast('Failed to toggle task', 'error');
  }
}

async function deleteTaskItem(id) {
  if (!confirm('Are you sure you want to delete this task?')) return;
  try {
    const res = await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.status === 'success') {
      showToast('Task removed from Second Brain', 'info');
      fetchTasks();
    }
  } catch (err) {
    showToast('Failed to delete task', 'error');
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
