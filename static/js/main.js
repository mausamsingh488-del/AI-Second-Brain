// ==========================================================================
// AI SECOND-BRAIN: GLOBAL CLIENT ENGINE
// Handles live clock, toasts, mobile sidebar toggle, and global notifications.
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  initClock();
  initSidebar();
  checkSystemStatus();
});

// Live Clock & Date in top navbar
function initClock() {
  const clockEl = document.getElementById('liveClock');
  if (!clockEl) return;

  function update() {
    const now = new Date();
    clockEl.textContent = now.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  }
  update();
  setInterval(update, 1000);
}

// Mobile sidebar drawer
function initSidebar() {
  const toggleBtn = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('mainSidebar');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('show');
    });

    // Close when clicking outside on mobile
    document.addEventListener('click', (e) => {
      if (window.innerWidth < 992 && !sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
        sidebar.classList.remove('show');
      }
    });
  }
}

// Global Toast notification utility
function showToast(message, type = 'info') {
  const toastEl = document.getElementById('appToast');
  const msgEl = document.getElementById('toastMessage');
  const iconEl = document.getElementById('toastIcon');

  if (!toastEl) return;

  msgEl.textContent = message;

  if (type === 'success') {
    iconEl.className = 'fa-solid fa-circle-check';
    iconEl.style.color = 'var(--color-secondary)';
  } else if (type === 'warning' || type === 'error') {
    iconEl.className = 'fa-solid fa-triangle-exclamation';
    iconEl.style.color = '#ff6b7b';
  } else {
    iconEl.className = 'fa-solid fa-circle-info';
    iconEl.style.color = 'var(--color-primary)';
  }

  const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
  toast.show();
}

// Check real status of Ollama & Whisper from backend
async function checkSystemStatus() {
  try {
    const res = await fetch('/api/stats');
    if (!res.ok) return;
    const data = await res.json();
    if (data.status === 'success' && data.system_status) {
      const ollamaText = document.getElementById('navOllamaStatus');
      const ollamaDot = document.getElementById('navOllamaDot');
      if (ollamaText && data.system_status.ollama) {
        ollamaText.textContent = `Ollama: ${data.system_status.ollama_connected ? 'Local' : 'Demo'}`;
        if (ollamaDot) {
          ollamaDot.className = data.system_status.ollama_connected ? 'status-dot status-dot-green' : 'status-dot status-dot-amber';
        }
      }
    }
  } catch (err) {
    console.debug('Status check caught offline condition:', err);
  }
}
