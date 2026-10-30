// ==========================================================================
// AI SECOND-BRAIN: GITHUB PORTFOLIO & STREAM CONTROLLER
// Renders GitHub profile stats, 365-day contribution heatmap, and activity feed.
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  loadGitHubProfile();
});

async function loadGitHubProfile() {
  try {
    const res = await fetch('/api/github');
    const data = await res.json();
    if (data.status !== 'success' || !data.github) throw new Error('Failed to load GitHub data');

    const gh = data.github;
    const nameEl = document.getElementById('ghName');
    if (nameEl) nameEl.textContent = gh.name || gh.username;
    
    const loginEl = document.getElementById('ghLogin');
    if (loginEl) loginEl.textContent = `@${gh.username}`;

    const bioEl = document.getElementById('ghBio');
    if (bioEl) bioEl.textContent = gh.bio;

    const avatarEl = document.getElementById('ghAvatar');
    if (avatarEl && gh.avatar_url) avatarEl.src = gh.avatar_url;

    const reposEl = document.getElementById('ghReposCount');
    if (reposEl) reposEl.textContent = gh.public_repos;

    const followEl = document.getElementById('ghFollowersCount');
    if (followEl) followEl.textContent = gh.followers;

    const streakEl = document.getElementById('ghStreakCount');
    if (streakEl) streakEl.textContent = `${gh.current_streak}d`;

    const summaryEl = document.getElementById('ghTotalCommitsSummary');
    if (summaryEl) summaryEl.textContent = `${gh.total_commits} commits recorded in past 365 days`;

    const statusBadge = document.getElementById('ghStatusBadge');
    if (statusBadge) statusBadge.textContent = gh.is_demo ? 'Demo Portfolio' : 'Live Sync';

    // Render Heatmap
    renderHeatmap(gh.heatmap);

    // Render Repositories
    renderRepos(gh.repositories || []);

    // Render Activities
    renderActivities(gh.recent_activity || []);

  } catch (err) {
    console.error('Error in GitHub dashboard:', err);
    showToast('Failed to load GitHub data', 'warning');
  }
}

function renderHeatmap(heatmapData) {
  const container = document.getElementById('ghHeatmapGrid');
  if (!container) return;

  if (!heatmapData || !heatmapData.weeks) {
    container.innerHTML = `<div class="text-muted text-center py-3">Heatmap unavailable</div>`;
    return;
  }

  container.innerHTML = heatmapData.weeks.map(week => `
    <div class="heatmap-week">
      ${week.map(day => `
        <div class="heatmap-day heatmap-lvl-${day.level}" title="${day.date}: ${day.count} commits"></div>
      `).join('')}
    </div>
  `).join('');
}

function renderRepos(repos) {
  const container = document.getElementById('ghReposGrid');
  if (!container) return;

  if (repos.length === 0) {
    container.innerHTML = `<div class="text-muted text-center py-3">No repositories found</div>`;
    return;
  }

  container.innerHTML = repos.map(r => `
    <div class="col-md-6 col-12">
      <div class="p-3 rounded glass-panel h-100 d-flex flex-column justify-content-between" style="background: rgba(30, 22, 16, 0.7); border: 1px solid rgba(213, 133, 31, 0.18);">
        <div>
          <div class="d-flex align-items-center justify-content-between mb-1">
            <h6 class="fw-bold mb-0 text-white font-mono" style="font-size: 0.9rem;">
              <i class="fa-regular fa-folder me-2" style="color: var(--color-primary);"></i>${r.name}
            </h6>
            <span class="badge" style="background: rgba(90, 62, 43, 0.5); font-size: 0.68rem; color: #ffca7b;">${r.language || 'Code'}</span>
          </div>
          <p class="text-muted mb-3" style="font-size: 0.78rem; line-height: 1.4;">
            ${r.description}
          </p>
        </div>

        <div class="d-flex align-items-center justify-content-between pt-2 border-top" style="border-color: rgba(90, 62, 43, 0.3) !important;">
          <div class="d-flex align-items-center gap-3 text-muted font-mono" style="font-size: 0.72rem;">
            <span><i class="fa-regular fa-star me-1 text-warning"></i>${r.stars}</span>
            <span><i class="fa-solid fa-code-fork me-1"></i>${r.forks}</span>
          </div>
          <a href="${r.html_url}" target="_blank" class="btn btn-sm btn-link text-decoration-none p-0" style="color: var(--color-primary); font-size: 0.75rem;">
            View Repo <i class="fa-solid fa-arrow-up-right-from-square ms-1"></i>
          </a>
        </div>
      </div>
    </div>
  `).join('');
}

function renderActivities(acts) {
  const container = document.getElementById('ghActivityFeed');
  if (!container) return;

  if (acts.length === 0) {
    container.innerHTML = `<div class="text-muted text-center py-3">No recent activities</div>`;
    return;
  }

  container.innerHTML = acts.map(a => `
    <div class="p-2 rounded" style="background: rgba(45, 33, 23, 0.3); border-left: 3px solid var(--color-secondary);">
      <div class="d-flex justify-content-between align-items-center">
        <span class="font-mono text-white fw-bold" style="font-size: 0.75rem;">${a.repo}</span>
        <span class="text-muted font-mono" style="font-size: 0.68rem;">${a.time}</span>
      </div>
      <p class="text-muted mb-0 mt-1" style="font-size: 0.78rem;">
        <span class="badge font-mono me-1" style="background: rgba(90, 62, 43, 0.6); font-size: 0.65rem;">${a.sha}</span>
        ${a.message}
      </p>
    </div>
  `).join('');
}
