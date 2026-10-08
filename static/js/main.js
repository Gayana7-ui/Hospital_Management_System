/* Global helpers for Hospital & Blood Bank Management System */

function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute('content') : '';
}

async function apiFetch(url, options = {}) {
  const opts = { ...options };
  opts.headers = {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCsrfToken(),
    ...(options.headers || {}),
  };
  if (opts.body && typeof opts.body === 'object') {
    opts.body = JSON.stringify(opts.body);
  }
  const res = await fetch(url, opts);
  let data;
  try {
    data = await res.json();
  } catch (e) {
    throw new Error('Invalid server response');
  }
  if (!res.ok || data.success === false) {
    throw new Error(data.message || 'Request failed');
  }
  return data;
}

function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = message;
  container.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

function confirmAction(message) {
  return window.confirm(message);
}

function badgeClass(status) {
  if (!status) return 'badge-muted';
  const s = status.toLowerCase();
  if (['available', 'paid', 'completed', 'confirmed', 'answered', 'active', 'eligible'].includes(s)) {
    return 'badge-success';
  }
  if (['pending', 'waiting', 'partially paid', 'partially available', 'emergency only'].includes(s)) {
    return 'badge-warning';
  }
  if (['cancelled', 'not available', 'on leave', 'unavailable', 'danger'].includes(s)) {
    return 'badge-danger';
  }
  return 'badge-info';
}

function toggleSidebar() {
  document.querySelector('.sidebar')?.classList.toggle('open');
  document.querySelector('.sidebar-overlay')?.classList.toggle('open');
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-confirm]').forEach((el) => {
    el.addEventListener('click', (e) => {
      if (!confirmAction(el.getAttribute('data-confirm'))) {
        e.preventDefault();
      }
    });
  });

  // Auto-hide flash messages
  setTimeout(() => {
    document.querySelectorAll('.flash-wrap .alert').forEach((a) => {
      a.style.opacity = '0';
      a.style.transition = 'opacity 0.4s';
      setTimeout(() => a.remove(), 400);
    });
  }, 4000);
});
