// ==========================================================================
// AI SECOND-BRAIN: ESP32 HARDWARE CONTROLLER
// Handles live polling, OLED display text update, mic testing, and serial console.
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  pollDeviceStatus();
  setInterval(pollDeviceStatus, 4000);
});

async function pollDeviceStatus() {
  try {
    const res = await fetch('/api/device/status');
    const data = await res.json();
    if (data.status !== 'success' || !data.device) return;

    const dev = data.device;
    const nameEl = document.getElementById('devName');
    if (nameEl) nameEl.textContent = dev.device_name;

    const ipEl = document.getElementById('devIp');
    if (ipEl) ipEl.textContent = `IP: ${dev.ip_address} • Wi-Fi: ${dev.wifi_ssid}`;

    const modeBadge = document.getElementById('devModeBadge');
    if (modeBadge) modeBadge.textContent = dev.mode || 'Simulation Mode';

    const batEl = document.getElementById('devBattery');
    if (batEl) batEl.textContent = `${dev.battery_level}%`;

    const oledBat = document.getElementById('oledBatVal');
    if (oledBat) oledBat.textContent = `BAT: ${dev.battery_level}%`;

    const rssiEl = document.getElementById('devRssi');
    if (rssiEl) rssiEl.textContent = `${dev.signal_strength} dBm`;

    const ssidEl = document.getElementById('devSsid');
    if (ssidEl) ssidEl.textContent = dev.wifi_ssid;

    const tempEl = document.getElementById('devTemp');
    if (tempEl) tempEl.textContent = `${dev.temperature} °C`;
    
    // Format uptime
    const s = dev.uptime_seconds;
    const hrs = String(Math.floor(s / 3600)).padStart(2, '0');
    const mins = String(Math.floor((s % 3600) / 60)).padStart(2, '0');
    const secs = String(s % 60).padStart(2, '0');
    const uptimeEl = document.getElementById('devUptime');
    if (uptimeEl) uptimeEl.textContent = `${hrs}:${mins}:${secs}`;

    const syncEl = document.getElementById('devLastSync');
    if (syncEl) syncEl.textContent = `Last sync: ${dev.last_sync || 'Live'}`;

    // OLED text
    const oledMain = document.getElementById('oledMainText');
    if (oledMain) oledMain.textContent = dev.lcd_text || 'AI Second Brain: Ready';

    // Terminal logs
    if (dev.logs && dev.logs.length > 0) {
      const term = document.getElementById('hardwareTerminalLogs');
      if (term) {
        term.innerHTML = dev.logs.map(l => `
          <div>
            <span style="color: #6D6257;">[${l.time}]</span>
            <span style="color: ${l.level === 'WARN' ? '#ffb04f' : (l.level === 'INFO' ? 'var(--color-secondary)' : '#ff6b7b')}; font-weight: bold;">[${l.level}]</span>
            <span class="text-white">${l.msg}</span>
          </div>
        `).join('');
        term.scrollTop = term.scrollHeight;
      }
    }

  } catch (err) {
    console.debug('Device status poll caught:', err);
  }
}

async function triggerAction(actionName) {
  try {
    const res = await fetch('/api/device/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: actionName })
    });
    const data = await res.json();
    if (data.status === 'success') {
      showToast(data.message, 'success');

      if (actionName === 'test_mic' && data.details) {
        const box = document.getElementById('micTestResultBox');
        if (box) {
          box.classList.remove('d-none');
          box.innerHTML = `
            <div class="p-2 rounded mt-2" style="background: rgba(20, 15, 11, 0.8);">
              <strong class="text-success"><i class="fa-solid fa-check me-1"></i>${data.message}</strong><br>
              Rate: ${data.details.sampling_rate} | Bit Depth: ${data.details.bit_depth} | SNR: ${data.details.snr}
            </div>
          `;
        }
      }

      pollDeviceStatus();
    } else {
      showToast(data.message, 'error');
    }
  } catch (err) {
    showToast('Failed to trigger device action', 'error');
  }
}

async function sendLcdMessage() {
  const input = document.getElementById('customLcdInput');
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;

  try {
    const res = await fetch('/api/device/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'test_lcd', text: text })
    });
    const data = await res.json();
    if (data.status === 'success') {
      showToast('OLED Display updated!', 'success');
      const oledMain = document.getElementById('oledMainText');
      if (oledMain) oledMain.textContent = text;
      input.value = '';
      pollDeviceStatus();
    }
  } catch (err) {
    showToast('Failed to send text to OLED', 'error');
  }
}
