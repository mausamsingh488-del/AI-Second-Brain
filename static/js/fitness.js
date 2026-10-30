// ==========================================================================
// AI SECOND-BRAIN: FITNESS & GYM TRACKER CONTROLLER
// Handles workout logging, Chart.js calories chart, PR tracking, and CRUD.
// ==========================================================================

let fitnessChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
  const todayStr = new Date().toISOString().split('T')[0];
  const dateInput = document.getElementById('newExDate');
  if (dateInput) dateInput.value = todayStr;

  fetchFitnessData();
});

async function fetchFitnessData() {
  const tbody = document.getElementById('fitnessLogsTable');
  try {
    const res = await fetch('/api/fitness');
    const data = await res.json();
    if (data.status !== 'success') throw new Error(data.message);

    const s = data.stats || {};
    const weekCountEl = document.getElementById('fitWeeklyCount');
    if (weekCountEl) weekCountEl.textContent = `${s.weekly_workouts} Sessions`;

    const calEl = document.getElementById('fitTotalCalories');
    if (calEl) calEl.textContent = `${s.total_calories} kcal`;

    const minEl = document.getElementById('fitTotalMinutes');
    if (minEl) minEl.textContent = `${s.total_duration_minutes} mins`;

    // Render Table
    if (tbody) {
      if (!data.workouts || data.workouts.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-muted">No workout logs yet. Record your first exercise session!</td></tr>`;
      } else {
        tbody.innerHTML = data.workouts.map(w => `
          <tr class="border-bottom" style="border-color: rgba(90, 62, 43, 0.25) !important;">
            <td class="text-white fw-semibold" style="font-size: 0.88rem;">${escapeHtml(w.exercise_name)}</td>
            <td><span class="badge" style="background: rgba(90, 62, 43, 0.5); color: #ffca7b; font-size: 0.72rem;">${w.category}</span></td>
            <td class="font-mono text-white" style="font-size: 0.82rem;">${w.sets} × ${w.reps}</td>
            <td class="font-mono" style="color: var(--color-primary); font-size: 0.82rem;">${w.weight} kg</td>
            <td class="text-muted font-mono" style="font-size: 0.8rem;">${w.duration_minutes}m</td>
            <td class="font-mono" style="color: var(--color-secondary); font-size: 0.82rem;">${w.calories_burned} kcal</td>
            <td class="text-muted font-mono" style="font-size: 0.8rem;">${w.workout_date}</td>
            <td>
              <button class="btn btn-sm btn-dark text-danger p-1" title="Delete record" onclick="deleteWorkout(${w.id})">
                <i class="fa-solid fa-trash-can" style="font-size: 0.75rem;"></i>
              </button>
            </td>
          </tr>
        `).join('');
      }
    }

    renderFitnessChart();
  } catch (err) {
    if (tbody) tbody.innerHTML = `<tr><td colspan="8" class="text-danger text-center py-3">Error loading fitness data</td></tr>`;
  }
}

async function renderFitnessChart() {
  const chartCanvas = document.getElementById('fitnessChart');
  if (!chartCanvas) return;

  try {
    const res = await fetch('/api/analytics');
    const data = await res.json();
    if (data.status !== 'success') return;

    const ctx = chartCanvas.getContext('2d');
    if (fitnessChartInstance) fitnessChartInstance.destroy();

    const grad = ctx.createLinearGradient(0, 0, 0, 200);
    grad.addColorStop(0, '#D5851F');
    grad.addColorStop(1, '#5A3E2B');

    fitnessChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [{
          label: 'Calories Burned (kcal)',
          data: data.calories_trend,
          backgroundColor: grad,
          borderRadius: 6,
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#C5BAAF', font: { family: 'Outfit', size: 11 } } },
          tooltip: { backgroundColor: 'rgba(25, 18, 13, 0.95)', borderColor: '#D5851F', borderWidth: 1 }
        },
        scales: {
          x: { grid: { color: 'rgba(90, 62, 43, 0.2)' }, ticks: { color: '#9E9185' } },
          y: { grid: { color: 'rgba(90, 62, 43, 0.2)' }, ticks: { color: '#9E9185' } }
        }
      }
    });
  } catch (err) {
    console.error('Error rendering fitness chart:', err);
  }
}

async function handleCreateWorkout(e) {
  e.preventDefault();
  const payload = {
    exercise_name: document.getElementById('newExName').value.trim(),
    category: document.getElementById('newExCategory').value,
    workout_date: document.getElementById('newExDate').value,
    sets: document.getElementById('newExSets').value,
    reps: document.getElementById('newExReps').value,
    weight: document.getElementById('newExWeight').value,
    duration_minutes: document.getElementById('newExDuration').value,
    calories_burned: document.getElementById('newExCalories').value,
    notes: document.getElementById('newExNotes').value.trim()
  };

  try {
    const res = await fetch('/api/fitness', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.status === 'success') {
      showToast('Workout session logged!', 'success');
      document.getElementById('createWorkoutForm').reset();
      bootstrap.Modal.getInstance(document.getElementById('addWorkoutModal')).hide();
      fetchFitnessData();
    }
  } catch (err) {
    showToast('Failed to log workout', 'error');
  }
}

async function deleteWorkout(id) {
  if (!confirm('Are you sure you want to delete this workout record?')) return;
  try {
    const res = await fetch(`/api/fitness/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.status === 'success') {
      showToast('Workout log removed', 'info');
      fetchFitnessData();
    }
  } catch (err) {
    showToast('Failed to delete workout', 'error');
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
