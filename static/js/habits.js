// ==========================================================================
// AI SECOND-BRAIN: HABITS CONTROLLER
// Handles habit tracking, 7-day pill grid, streak recalculation, and modal creations.
// ==========================================================================

let allHabits = [];

document.addEventListener('DOMContentLoaded', () => {
  fetchHabits();
});

async function fetchHabits() {
  const container = document.getElementById('habitsContainer');
  try {
    const res = await fetch('/api/habits');
    const data = await res.json();
    if (data.status !== 'success') throw new Error(data.message);

    allHabits = data.habits || [];
    renderHabits();
  } catch (err) {
    if (container) {
      container.innerHTML = `<div class="col-12 text-center text-danger py-4">Error loading habits: ${err.message}</div>`;
    }
  }
}

function renderHabits() {
  const container = document.getElementById('habitsContainer');
  if (!container) return;

  if (allHabits.length === 0) {
    container.innerHTML = `
      <div class="col-12 text-center py-5 text-muted">
        <i class="fa-solid fa-fire-burner mb-2" style="font-size: 2rem;"></i>
        <div>No habits tracked yet. Click "Track New Habit" above!</div>
      </div>
    `;
    return;
  }

  // Update counts
  const doneTodayCount = allHabits.filter(h => h.completed_today).length;
  const ratioEl = document.getElementById('todayDoneRatioLabel');
  if (ratioEl) ratioEl.textContent = `${doneTodayCount} / ${allHabits.length}`;

  const maxStreak = Math.max(...allHabits.map(h => h.best_streak || h.current_streak), 0);
  const streakEl = document.getElementById('longestStreakLabel');
  if (streakEl) streakEl.textContent = `${maxStreak} Days`;

  container.innerHTML = allHabits.map(h => {
    // 7 days pills
    const pastDaysHtml = (h.past_7_days || []).map(d => {
      const dayDate = new Date(d.date);
      const dayLetter = dayDate.toLocaleDateString('en-US', { weekday: 'narrow' });
      return `
        <div class="d-flex flex-column align-items-center gap-1 cursor-pointer" onclick="toggleHabitSpecificDate(${h.id}, '${d.date}')" title="${d.date}: ${d.completed ? 'Completed' : 'Missed'}">
          <span style="font-size: 0.65rem; color: #8E8276;">${dayLetter}</span>
          <div class="rounded-circle d-flex align-items-center justify-content-center" style="width: 28px; height: 28px; background: ${d.completed ? 'var(--color-secondary)' : 'rgba(90, 62, 43, 0.4)'}; border: 1px solid ${d.completed ? 'var(--color-secondary)' : 'rgba(90, 62, 43, 0.6)'};">
            <i class="fa-solid fa-check text-dark" style="font-size: 0.7rem; opacity: ${d.completed ? '1' : '0'};"></i>
          </div>
        </div>
      `;
    }).join('');

    return `
      <div class="col-lg-6 col-12">
        <div class="glass-panel p-4 h-100 ${h.completed_today ? 'glass-card-green' : ''}" style="background: rgba(32, 24, 18, 0.8);">
          <div class="d-flex align-items-start justify-content-between mb-3">
            <div class="d-flex align-items-center gap-3">
              <div class="brand-icon" style="background: ${h.completed_today ? 'linear-gradient(135deg, var(--color-secondary), #5a7d42)' : 'rgba(90, 62, 43, 0.5)'}; color: #fff;">
                <i class="fa-solid ${h.icon || 'fa-check'}"></i>
              </div>
              <div>
                <h5 class="fw-bold text-white mb-0" style="font-size: 1.05rem;">${escapeHtml(h.name)}</h5>
                <small class="text-muted" style="font-size: 0.78rem;">${escapeHtml(h.description || h.category)}</small>
              </div>
            </div>

            <!-- Streak badge -->
            <div class="text-end">
              <span class="badge" style="background: rgba(213, 133, 31, 0.2); color: var(--color-primary); border: 1px solid var(--color-primary); font-size: 0.82rem;">
                <i class="fa-solid fa-fire me-1"></i>${h.current_streak} Day Streak
              </span>
              <div class="text-muted mt-1" style="font-size: 0.7rem;">Best: ${h.best_streak}d</div>
            </div>
          </div>

          <!-- 7-Day History Track -->
          <div class="d-flex align-items-center justify-content-between p-3 rounded mb-3" style="background: rgba(20, 15, 11, 0.7); border: 1px solid rgba(90, 62, 43, 0.3);">
            <div class="d-flex gap-2">
              ${pastDaysHtml}
            </div>
            <div>
              <button class="btn btn-sm ${h.completed_today ? 'btn-secondary-brain' : 'btn-outline-brain'}" onclick="toggleHabitToday(${h.id})">
                <i class="fa-solid ${h.completed_today ? 'fa-check-circle' : 'fa-circle-plus'} me-1"></i>
                ${h.completed_today ? 'Completed Today' : 'Check Today'}
              </button>
            </div>
          </div>

          <div class="d-flex justify-content-between align-items-center">
            <span class="badge" style="background: rgba(90, 62, 43, 0.4); color: #c5baaf; font-size: 0.72rem;">${h.category}</span>
            <button class="btn btn-sm btn-link text-muted p-0" title="Delete habit" onclick="deleteHabit(${h.id})">
              <i class="fa-solid fa-trash-can" style="font-size: 0.75rem;"></i>
            </button>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

async function handleCreateHabit(e) {
  e.preventDefault();
  const payload = {
    name: document.getElementById('newHabitName').value.trim(),
    description: document.getElementById('newHabitDesc').value.trim(),
    category: document.getElementById('newHabitCategory').value,
    icon: document.getElementById('newHabitIcon').value
  };

  try {
    const res = await fetch('/api/habits', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.status === 'success') {
      showToast('New habit added!', 'success');
      document.getElementById('createHabitForm').reset();
      bootstrap.Modal.getInstance(document.getElementById('addHabitModal')).hide();
      fetchHabits();
    }
  } catch (err) {
    showToast('Failed to create habit', 'error');
  }
}

async function toggleHabitToday(id) {
  try {
    const res = await fetch(`/api/habits/${id}/toggle`, { method: 'POST' });
    const data = await res.json();
    if (data.status === 'success') {
      showToast(data.completed ? 'Habit completed today! Streak updated!' : 'Habit marked pending for today.', 'success');
      fetchHabits();
    }
  } catch (err) {
    showToast('Failed to toggle habit', 'error');
  }
}

async function toggleHabitSpecificDate(id, targetDate) {
  try {
    const res = await fetch(`/api/habits/${id}/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date: targetDate })
    });
    const data = await res.json();
    if (data.status === 'success') {
      fetchHabits();
    }
  } catch (err) {
    showToast('Failed to update date log', 'error');
  }
}

async function deleteHabit(id) {
  if (!confirm('Are you sure you want to delete this habit and its history?')) return;
  try {
    const res = await fetch(`/api/habits/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.status === 'success') {
      showToast('Habit deleted', 'info');
      fetchHabits();
    }
  } catch (err) {
    showToast('Failed to delete habit', 'error');
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
