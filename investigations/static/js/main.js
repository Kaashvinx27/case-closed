/**
 * CASE CLOSED: Core Utilities, Audio Engine, & CSRF Helper
 */

// Web Audio API Synthesizer (Zero-dependency, offline sound effects)
class BureauAudioEngine {
  constructor() {
    this.ctx = null;
    this.enabled = localStorage.getItem('case_closed_audio') === 'true';
  }

  init() {
    if (!this.ctx && (window.AudioContext || window.webkitAudioContext)) {
      this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    }
  }

  toggle(enable) {
    this.enabled = enable !== undefined ? enable : !this.enabled;
    localStorage.setItem('case_closed_audio', this.enabled ? 'true' : 'false');
    const toggleBtn = document.getElementById('bureau-audio-toggle');
    if (toggleBtn) {
      toggleBtn.innerHTML = this.enabled ? 
        '<i class="bi bi-volume-up-fill text-gold"></i>' : 
        '<i class="bi bi-volume-mute text-muted"></i>';
    }
    return this.enabled;
  }

  playClick() {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(440, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(120, this.ctx.currentTime + 0.05);
      gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.05);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.05);
    } catch(e) {}
  }

  playDiscovery() {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    try {
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(587.33, now); // D5
      osc.frequency.setValueAtTime(880, now + 0.1); // A5
      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.35);
    } catch(e) {}
  }

  playContradiction() {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    try {
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(220, now);
      osc.frequency.linearRampToValueAtTime(110, now + 0.3);
      gain.gain.setValueAtTime(0.18, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.35);
    } catch(e) {}
  }
}

window.bureauAudio = new BureauAudioEngine();

// HTML string escaping helper
function escapeHTML(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// CSRF Cookie extraction helper for Fetch API
function getCsrfToken() {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// In-app Toast notifier
function showBureauToast(title, message, type = 'gold') {
  const container = document.getElementById('bureau-toast-container');
  if (!container) return;

  const toastId = 'toast-' + Math.random().toString(36).substring(2, 9);
  const borderCol = type === 'crimson' ? 'border-danger' : (type === 'success' ? 'border-success' : 'border-warning');
  const icon = type === 'crimson' ? 'exclamation-octagon-fill text-danger' : (type === 'success' ? 'check-circle-fill text-success' : 'shield-fill-check text-warning');

  const toastEl = document.createElement('div');
  toastEl.className = `toast toast-bureau border ${borderCol} mb-2 show`;
  toastEl.id = toastId;
  toastEl.setAttribute('role', 'alert');
  toastEl.innerHTML = `
    <div class="toast-header bg-dark text-light border-bottom border-secondary">
      <i class="bi bi-${icon} me-2"></i>
      <strong class="me-auto font-mono text-uppercase">${title}</strong>
      <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
    <div class="toast-body small">
      ${message}
    </div>
  `;
  container.appendChild(toastEl);

  setTimeout(() => {
    toastEl.remove();
  }, 4500);
}

document.addEventListener('DOMContentLoaded', () => {
  // Initialize audio toggle button state
  const audioToggle = document.getElementById('bureau-audio-toggle');
  if (audioToggle) {
    audioToggle.innerHTML = window.bureauAudio.enabled ? 
      '<i class="bi bi-volume-up-fill text-gold"></i>' : 
      '<i class="bi bi-volume-mute text-muted"></i>';
    audioToggle.addEventListener('click', (e) => {
      e.preventDefault();
      window.bureauAudio.toggle();
    });
  }

  // Add click sounds to bureau buttons
  document.querySelectorAll('.btn-crimson, .btn-outline-gold, .btn-bureau-secondary').forEach(btn => {
    btn.addEventListener('click', () => {
      window.bureauAudio.playClick();
    });
  });
});
