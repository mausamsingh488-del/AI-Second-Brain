// ==========================================================================
// AI SECOND-BRAIN: DASHBOARD CONTROLLER
// Loads telemetry, renders Chart.js visualizations, and handles quick actions.
// ==========================================================================

let productivityChartInstance = null;
let categoryChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
  loadDashboardStats();
  loadDashboardCharts();
  loadTodayTasks();
  loadDashboardReminders();
  loadDashboardHabits();
});

// Load KPI counts and system flags
async function loadDashboardStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    if (data.status !== 'success') return;

    const s = data.stats;
    document.getElementById('kpiTasksCompleted').textContent = s.tasks_completed;
    document.getElementById('kpiTasksPending').textContent = s.tasks_pending;
    document.getElementById('kpiActiveHabits').textContent = s.active_habits;
    document.getElementById('kpiHabitsDoneToday').textContent = s.habits_completed_today;
    document.getElementById('kpiGithubCommits').textContent = s.github_commits;
    document.getElementById('kpiWorkouts').textContent = s.workout_sessions;
    document.getElementById('kpiCalories').textContent = s.calories_burned;
    document.getElementById('kpiVoiceNotes').textContent = `${s.voice_notes} Captured`;
    document.getElementById('kpiAiMemories').textContent = `${s.ai_memories} Entries`;

    // System status labels
    const sys = data.system_status;
    document.getElementById('statOllamaText').textContent = sys.ollama_connected ? 'Local Engine' : 'Demo Mode';
    document.getElementById('statWhisperText').textContent = sys.whisper_connected ? 'Local Whisper' : 'Demo Ready';
    document.getElementById('statEsp32Text').textContent = sys.esp32_connected ? (sys.esp32.includes('Physical') ? 'Physical Node' : 'Simulated') : 'Offline';
  } catch (err) {
    console.error('Error loading dashboard stats:', err);
  }
}

// Render Chart.js analytics
async function loadDashboardCharts() {
  try {
    const res = await fetch('/api/analytics');
    const data = await res.json();
    if (data.status !== 'success') return;

    if (data.average_score) {
      document.getElementById('chartAvgScore').textContent = data.average_score;
    }

    // 1. Productivity Trend Chart
    const ctxProd = document.getElementById('productivityChart').getContext('2d');
    
    // Gradients
    const gradPrimary = ctxProd.createLinearGradient(0, 0, 0, 250);
    gradPrimary.addColorStop(0, 'rgba(213, 133, 31, 0.45)');
    gradPrimary.addColorStop(1, 'rgba(213, 133, 31, 0.0)');

    const gradSecondary = ctxProd.createLinearGradient(0, 0, 0, 250);
    gradSecondary.addColorStop(0, 'rgba(135, 169, 107, 0.45)');
    gradSecondary.addColorStop(1, 'rgba(135, 169, 107, 0.0)');

    if (productivityChartInstance) productivityChartInstance.destroy();

    productivityChartInstance = new Chart(ctxProd, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [
          {
            label: 'Productivity Score',
            data: data.productivity_scores,
            borderColor: '#D5851F',
            backgroundColor: gradPrimary,
            fill: true,
            tension: 0.35,
            borderWidth: 3,
            pointBackgroundColor: '#D5851F',
            pointRadius: 4,
            yAxisID: 'y'
          },
          {
            label: 'Habits Completed',
            data: data.habits_trend,
            borderColor: '#87A96B',
            backgroundColor: gradSecondary,
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            borderDash: [5, 5],
            pointBackgroundColor: '#87A96B',
            pointRadius: 3,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: {
            labels: { color: '#C5BAAF', font: { family: 'Outfit', size: 12 } }
          },
          tooltip: {
            backgroundColor: 'rgba(25, 18, 13, 0.95)',
            borderColor: '#D5851F',
            borderWidth: 1,
            titleColor: '#fff',
            bodyColor: '#e0d8cf'
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(90, 62, 43, 0.2)' },
            ticks: { color: '#9E9185', font: { family: 'JetBrains Mono' } }
          },
          y: {
            type: 'linear',
            position: 'left',
            min: 20,
            max: 100,
            grid: { color: 'rgba(90, 62, 43, 0.2)' },
            ticks: { color: '#9E9185' }
          },
          y1: {
            type: 'linear',
            position: 'right',
            min: 0,
            max: 8,
            grid: { drawOnChartArea: false },
            ticks: { color: '#87A96B' }
          }
        }
      }
    });

    // 2. Category Doughnut Chart
    const ctxCat = document.getElementById('categoryChart').getContext('2d');
    if (categoryChartInstance) categoryChartInstance.destroy();

    categoryChartInstance = new Chart(ctxCat, {
      type: 'doughnut',
      data: {
        labels: data.categories.labels,
        datasets: [{
          data: data.categories.counts,
          backgroundColor: [
            '#D5851F', // Warm amber (College)
            '#ffb04f', // Light amber (Internship)
            '#87A96B', // Asparagus green (Coding)
            '#5A3E2B', // Coffee brown (Personal)
            '#a4ce82', // Light sage (Fitness)
            '#f3b15f'  // Ochre (GitHub)
          ],
          borderColor: '#16120e',
          borderWidth: 3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: '#C5BAAF', font: { family: 'Outfit', size: 11 }, boxWidth: 12 }
          }
        },
        cutout: '68%'
      }
    });
  } catch (err) {
    console.error('Error loading charts:', err);
  }
}

// Load today's task checklist
async function loadTodayTasks() {
  const container = document.getElementById('dashboardTasksList');
  try {
    const res = await fetch('/api/tasks');
    const data = await res.json();
    if (!data.tasks || data.tasks.length === 0) {
      container.innerHTML = `<div class="text-muted text-center py-3">No tasks found. Create your first task!</div>`;
      return;
    }

    // Show top 4 urgent/pending tasks first
    const tasksToShow = data.tasks.slice(0, 5);

    container.innerHTML = tasksToShow.map(t => `
      <div class="d-flex align-items-center justify-content-between p-3 rounded glass-panel" style="background: rgba(36, 26, 18, 0.6);">
        <div class="d-flex align-items-center gap-3">
          <input type="checkbox" class="form-check-input" style="width: 20px; height: 20px; cursor: pointer; accent-color: var(--color-primary);" ${t.completed ? 'checked' : ''} onchange="toggleTaskStatus(${t.id})">
          <div>
            <div class="fw-semibold text-white ${t.completed ? 'text-decoration-line-through text-muted' : ''}" style="font-size: 0.9rem;">
              ${escapeHtml(t.title)}
            </div>
            <div class="d-flex align-items-center gap-2 mt-1">
              <span class="badge" style="background: rgba(90, 62, 43, 0.5); font-size: 0.7rem; color: #ffca7b;">${t.category}</span>
              <span class="text-muted" style="font-size: 0.72rem;"><i class="fa-regular fa-calendar me-1"></i>${t.due_date || 'No date'}</span>
            </div>
          </div>
        </div>
        <span class="badge badge-priority-${t.priority.toLowerCase()}">${t.priority}</span>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = `<div class="text-danger py-2">Error loading tasks</div>`;
  }
}

// Toggle task status
async function toggleTaskStatus(taskId) {
  try {
    const res = await fetch(`/api/tasks/${taskId}/toggle`, { method: 'POST' });
    const data = await res.json();
    if (data.status === 'success') {
      showToast(data.message, 'success');
      loadTodayTasks();
      loadDashboardStats();
      loadDashboardCharts();
    }
  } catch (err) {
    showToast('Failed to update task', 'error');
  }
}

// Load upcoming reminders
async function loadDashboardReminders() {
  const container = document.getElementById('dashboardRemindersList');
  try {
    const res = await fetch('/api/reminders');
    const data = await res.json();
    if (!data.reminders || data.reminders.length === 0) {
      container.innerHTML = `<div class="text-muted text-center py-2">No upcoming reminders</div>`;
      return;
    }

    container.innerHTML = data.reminders.slice(0, 3).map(r => `
      <div class="d-flex align-items-center justify-content-between p-2 rounded" style="background: rgba(90, 62, 43, 0.2); border: 1px solid rgba(213, 133, 31, 0.15);">
        <div>
          <strong class="text-white d-block" style="font-size: 0.85rem;">${escapeHtml(r.title)}</strong>
          <small class="text-muted font-mono" style="font-size: 0.72rem;">
            <i class="fa-regular fa-clock me-1 text-warning"></i>${r.reminder_time} • ${r.reminder_date}
          </small>
        </div>
        <span class="badge ${r.status === 'Today' ? 'bg-warning text-dark' : 'bg-secondary'}">${r.status}</span>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = `<div class="text-danger py-2">Error loading reminders</div>`;
  }
}

// Load habits quick toggles
async function loadDashboardHabits() {
  const container = document.getElementById('dashboardHabitsList');
  try {
    const res = await fetch('/api/habits');
    const data = await res.json();
    if (!data.habits || data.habits.length === 0) {
      container.innerHTML = `<div class="text-muted text-center py-2">No habits tracked</div>`;
      return;
    }

    container.innerHTML = data.habits.slice(0, 4).map(h => `
      <div class="d-flex align-items-center justify-content-between p-2 rounded" style="background: rgba(45, 33, 23, 0.4); border: 1px solid rgba(135, 169, 107, 0.15);">
        <div class="d-flex align-items-center gap-2">
          <i class="fa-solid ${h.icon || 'fa-circle-check'}" style="color: var(--color-secondary);"></i>
          <span class="text-white" style="font-size: 0.85rem;">${escapeHtml(h.name)}</span>
        </div>
        <button class="btn btn-sm ${h.completed_today ? 'btn-secondary-brain' : 'btn-outline-brain'} py-0 px-2" style="font-size: 0.75rem;" onclick="toggleDashboardHabit(${h.id})">
          ${h.completed_today ? '<i class="fa-solid fa-check me-1"></i>Done' : 'Mark Today'}
        </button>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = `<div class="text-danger py-2">Error loading habits</div>`;
  }
}

// Toggle habit completion today
async function toggleDashboardHabit(habitId) {
  try {
    const res = await fetch(`/api/habits/${habitId}/toggle`, { method: 'POST' });
    const data = await res.json();
    if (data.status === 'success') {
      showToast(data.completed ? 'Habit completed today! Streak updated!' : 'Habit unchecked for today.', 'success');
      loadDashboardHabits();
      loadDashboardStats();
      loadDashboardCharts();
    }
  } catch (err) {
    showToast('Failed to toggle habit', 'error');
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
