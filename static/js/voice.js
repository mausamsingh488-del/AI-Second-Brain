// ==========================================================================
// AI SECOND-BRAIN: VOICE ASSISTANT CLIENT ENGINE
// Handles MediaRecorder audio capture, timer, visualizer, transcription API,
// AI entity extraction rendering, and saving to SQLite.
// ==========================================================================

let mediaRecorder = null;
let audioChunks = [];
let audioBlob = null;
let recordStartTime = null;
let timerInterval = null;
let isRecording = false;

// Cached parsed state
let currentExtractedData = null;

document.addEventListener('DOMContentLoaded', () => {
  loadVoiceNotesHistory();
});

async function toggleRecording() {
  if (isRecording) {
    stopRecording();
  } else {
    await startRecording();
  }
}

async function startRecording() {
  audioChunks = [];
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstop = () => {
      audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      const audioUrl = URL.createObjectURL(audioBlob);
      document.getElementById('audioPlayer').src = audioUrl;
      document.getElementById('audioPlaybackSection').classList.remove('d-none');
      
      // Stop microphone stream tracks to release hardware
      stream.getTracks().forEach(track => track.stop());
    };

    mediaRecorder.start();
    isRecording = true;

    // UI Updates
    const btn = document.getElementById('micRecordBtn');
    btn.classList.add('recording');
    document.getElementById('micIcon').className = 'fa-solid fa-stop';
    document.getElementById('recordingStatusPill').textContent = 'Listening to voice...';
    document.getElementById('recordingStatusPill').style.color = '#ff6b7b';

    // Start Timer
    recordStartTime = Date.now();
    timerInterval = setInterval(updateTimer, 500);

    // Waveform bounce
    animateWaveform(true);

  } catch (err) {
    console.warn('Microphone permission or hardware unavailable:', err);
    showToast('Microphone access unavailable or denied. Use demo presets below!', 'warning');
  }
}

function stopRecording() {
  if (mediaRecorder && isRecording) {
    mediaRecorder.stop();
    isRecording = false;
    clearInterval(timerInterval);

    // UI Updates
    const btn = document.getElementById('micRecordBtn');
    btn.classList.remove('recording');
    document.getElementById('micIcon').className = 'fa-solid fa-microphone';
    document.getElementById('recordingStatusPill').textContent = 'Audio captured cleanly';
    document.getElementById('recordingStatusPill').style.color = 'var(--color-secondary)';
    animateWaveform(false);
  }
}

function updateTimer() {
  const elapsed = Math.floor((Date.now() - recordStartTime) / 1000);
  const mins = String(Math.floor(elapsed / 60)).padStart(2, '0');
  const secs = String(elapsed % 60).padStart(2, '0');
  document.getElementById('recordingTimer').textContent = `${mins}:${secs}`;
}

function animateWaveform(active) {
  const bars = document.querySelectorAll('#waveformVisualizer div');
  if (active) {
    bars.forEach((b, idx) => {
      b.style.transition = 'height 0.2s ease';
      b.style.backgroundColor = 'var(--color-primary)';
      setInterval(() => {
        b.style.height = `${Math.floor(Math.random() * 24) + 6}px`;
      }, 200 + (idx * 50));
    });
  } else {
    bars.forEach(b => {
      b.style.height = '8px';
      b.style.backgroundColor = 'var(--color-secondary)';
    });
  }
}

function discardRecording() {
  audioBlob = null;
  document.getElementById('audioPlayer').src = '';
  document.getElementById('audioPlaybackSection').classList.add('d-none');
  document.getElementById('recordingTimer').textContent = '00:00';
  document.getElementById('recordingStatusPill').textContent = 'Ready to listen';
}

// Send real audio file to Whisper endpoint
async function sendRecordedAudio() {
  if (!audioBlob) return;
  const formData = new FormData();
  formData.append('audio', audioBlob, 'voice_recording.webm');

  showToast('Sending audio to Whisper STT...', 'info');

  try {
    const res = await fetch('/api/voice/transcribe', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    if (data.status === 'success') {
      displayParsedResult(data);
    } else {
      showToast('Transcription error: ' + data.message, 'error');
    }
  } catch (err) {
    showToast('Failed to transcribe audio', 'error');
  }
}

// Demo preset runner
async function testVoicePreset(presetText) {
  showToast('Simulating voice input: "' + presetText.substring(0, 30) + '..."', 'info');
  try {
    const res = await fetch('/api/voice/transcribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ simulated_text: presetText })
    });
    const data = await res.json();
    if (data.status === 'success') {
      displayParsedResult(data);
    }
  } catch (err) {
    showToast('Voice simulation failed', 'error');
  }
}

// Display Extracted Intelligence in Card
function displayParsedResult(data) {
  currentExtractedData = data;

  document.getElementById('aiPlaceholderPrompt').classList.add('d-none');
  const card = document.getElementById('aiParsedCard');
  card.classList.remove('d-none');

  document.getElementById('transcriptionModeBadge').textContent = data.mode || 'Whisper Mode';
  document.getElementById('cardRawTranscript').textContent = `"${data.transcript}"`;

  const ent = data.entities || {};
  document.getElementById('cardActionType').textContent = ent.action_type || 'Task';
  document.getElementById('cardTitle').textContent = ent.title || data.transcript;
  document.getElementById('cardCategory').textContent = ent.category || 'General';
  
  const prioBadge = document.getElementById('cardPriority');
  prioBadge.textContent = ent.priority || 'Medium';
  prioBadge.className = `badge badge-priority-${(ent.priority || 'Medium').toLowerCase()}`;

  document.getElementById('cardDate').textContent = ent.date || 'Today';
  document.getElementById('cardTime').textContent = ent.time || '10:00 AM';

  showToast('Entities extracted successfully!', 'success');
}

// Commit voice note to DB (and auto-create task/reminder/workout)
async function commitVoiceNoteToDb() {
  if (!currentExtractedData) return;
  try {
    const res = await fetch('/api/voice/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        transcript: currentExtractedData.transcript,
        entities: currentExtractedData.entities,
        audio_path: currentExtractedData.audio_path,
        auto_create: true
      })
    });
    const data = await res.json();
    if (data.status === 'success') {
      showToast(data.message, 'success');
      loadVoiceNotesHistory();
      // Reset card after short delay
      setTimeout(() => {
        document.getElementById('aiParsedCard').classList.add('d-none');
        document.getElementById('aiPlaceholderPrompt').classList.remove('d-none');
        discardRecording();
      }, 1500);
    }
  } catch (err) {
    showToast('Failed to save voice note', 'error');
  }
}

// Load Voice Notes History
async function loadVoiceNotesHistory() {
  const tbody = document.getElementById('voiceNotesHistoryTable');
  try {
    const res = await fetch('/api/voice/notes');
    const data = await res.json();
    if (!data.notes || data.notes.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" class="text-center py-3 text-muted">No voice notes recorded yet.</td></tr>`;
      return;
    }

    document.getElementById('voiceNoteCountLabel').textContent = `${data.notes.length} Notes Recorded`;

    tbody.innerHTML = data.notes.map(n => `
      <tr class="border-bottom" style="border-color: rgba(90, 62, 43, 0.2) !important;">
        <td class="text-white" style="font-size: 0.85rem;">
          <i class="fa-solid fa-quote-left text-muted me-2" style="font-size: 0.7rem;"></i>
          ${escapeHtml(n.transcript)}
        </td>
        <td>
          <span class="badge" style="background: rgba(213, 133, 31, 0.2); color: var(--color-primary); border: 1px solid var(--color-primary); font-size: 0.72rem;">
            ${n.action_type}
          </span>
        </td>
        <td class="text-muted font-mono" style="font-size: 0.75rem;">
          ${n.created_at ? new Date(n.created_at).toLocaleString() : 'Recent'}
        </td>
        <td>
          <span class="badge" style="background: rgba(135, 169, 107, 0.2); color: var(--color-secondary); font-size: 0.72rem;">
            <i class="fa-solid fa-check me-1"></i>${n.status}
          </span>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="4" class="text-danger py-2">Error loading voice notes</td></tr>`;
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
