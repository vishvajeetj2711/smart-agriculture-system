/**
 * Smart Agriculture System — Main JavaScript
 * Handles: form UX, loading spinners, auto-weather refresh,
 * Chart.js helpers, upload previews, and general UI polish.
 */

'use strict';

/* ── DOM Ready ─────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {
  initFormSpinners();
  initTooltips();
  initAutoFadeAlerts();
  highlightActiveNav();
  initNumberInputValidation();
});

/* ═══════════════════════════════════════════════════════════════
   1. FORM SUBMIT — Loading Spinner
═══════════════════════════════════════════════════════════════ */
function initFormSpinners() {
  const forms = document.querySelectorAll('form[method="POST"]');
  forms.forEach(form => {
    form.addEventListener('submit', function (e) {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (!submitBtn) return;
      // Skip if button already handles its own spinner (disease page)
      if (submitBtn.id === 'detectBtn') return;
      const origText = submitBtn.innerHTML;
      submitBtn.innerHTML =
        '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing...';
      submitBtn.disabled = true;
      // Re-enable after 15s as safety fallback
      setTimeout(() => {
        submitBtn.innerHTML = origText;
        submitBtn.disabled  = false;
      }, 15000);
    });
  });
}

/* ═══════════════════════════════════════════════════════════════
   2. BOOTSTRAP TOOLTIPS
═══════════════════════════════════════════════════════════════ */
function initTooltips() {
  const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipEls.forEach(el => new bootstrap.Tooltip(el, { trigger: 'hover' }));
}

/* ═══════════════════════════════════════════════════════════════
   3. AUTO-FADE ALERTS after 6 seconds
═══════════════════════════════════════════════════════════════ */
function initAutoFadeAlerts() {
  const alerts = document.querySelectorAll('.alert.alert-success, .alert.alert-info');
  alerts.forEach(alert => {
    // Only auto-fade standalone dismissible alerts (not result blocks)
    if (!alert.querySelector('.btn-close')) return;
    setTimeout(() => {
      alert.style.transition = 'opacity 0.8s';
      alert.style.opacity    = '0';
      setTimeout(() => alert.remove(), 800);
    }, 6000);
  });
}

/* ═══════════════════════════════════════════════════════════════
   4. HIGHLIGHT ACTIVE NAV LINK (backup in case Jinja misses)
═══════════════════════════════════════════════════════════════ */
function highlightActiveNav() {
  const path  = window.location.pathname;
  const links = document.querySelectorAll('.navbar .nav-link');
  links.forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '/' && path.startsWith(href)) {
      link.classList.add('active');
    } else if (href === '/' && path === '/') {
      link.classList.add('active');
    }
  });
}

/* ═══════════════════════════════════════════════════════════════
   5. NUMBER INPUT VALIDATION — prevent negative values
═══════════════════════════════════════════════════════════════ */
function initNumberInputValidation() {
  document.querySelectorAll('input[type="number"]').forEach(input => {
    input.addEventListener('input', function () {
      const min = parseFloat(this.min);
      const max = parseFloat(this.max);
      const val = parseFloat(this.value);
      if (!isNaN(min) && val < min) this.value = min;
      if (!isNaN(max) && val > max) this.value = max;
    });
  });
}

/* ═══════════════════════════════════════════════════════════════
   6. LIVE WEATHER FETCH (for dashboard weather widget)
═══════════════════════════════════════════════════════════════ */
function fetchLiveWeather(city, containerId) {
  if (!city || !containerId) return;
  const container = document.getElementById(containerId);
  if (!container) return;

  fetch(`/api/weather/${encodeURIComponent(city)}`)
    .then(r => r.ok ? r.json() : null)
    .then(data => {
      if (!data || !data.success) return;
      // Optionally update a temp display element
      const tempEl = container.querySelector('[data-weather-temp]');
      if (tempEl) tempEl.textContent = data.weather.temp + '°C';
      const humEl = container.querySelector('[data-weather-hum]');
      if (humEl) humEl.textContent = data.weather.humidity + '%';
    })
    .catch(() => {}); // silent fail
}

/* ═══════════════════════════════════════════════════════════════
   7. MARKET PRICE AJAX FETCH
═══════════════════════════════════════════════════════════════ */
function fetchMarketPrice(crop, state) {
  const resultArea = document.getElementById('marketResult');
  if (!resultArea) return;

  resultArea.innerHTML =
    '<div class="text-center py-4"><span class="spinner-border text-success"></span> ' +
    '<span class="ms-2 text-muted">Fetching mandi prices...</span></div>';

  fetch(`/api/market/${encodeURIComponent(crop)}/${encodeURIComponent(state)}`)
    .then(r => r.json())
    .then(data => {
      if (!data.success) {
        resultArea.innerHTML =
          `<div class="alert alert-danger">${data.error || 'Error fetching prices'}</div>`;
        return;
      }
      // Refresh page with POST is handled by form — this is for optional AJAX use
      resultArea.innerHTML =
        '<div class="alert alert-success">Prices loaded. Submit the form to view details.</div>';
    })
    .catch(() => {
      resultArea.innerHTML =
        '<div class="alert alert-warning">Could not fetch prices. Check your connection.</div>';
    });
}

/* ═══════════════════════════════════════════════════════════════
   8. CHART.JS — Default Global Config
═══════════════════════════════════════════════════════════════ */
if (typeof Chart !== 'undefined') {
  Chart.defaults.font.family = "'Poppins', sans-serif";
  Chart.defaults.font.size   = 12;
  Chart.defaults.color       = '#666';
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.tooltip.padding = 10;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
  Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(30,30,30,0.85)';
}

/* ═══════════════════════════════════════════════════════════════
   9. SOLAR LAND VALIDATION (backup for inline handler)
═══════════════════════════════════════════════════════════════ */
(function () {
  const totalIn  = document.getElementById('totalLand');
  const solarIn  = document.getElementById('solarLand');
  if (!totalIn || !solarIn) return;

  function check() {
    const total = parseFloat(totalIn.value) || 0;
    const solar = parseFloat(solarIn.value) || 0;
    if (solar >= total && total > 0) {
      solarIn.setCustomValidity('Solar land must be less than total land');
    } else {
      solarIn.setCustomValidity('');
    }
  }
  totalIn.addEventListener('input', check);
  solarIn.addEventListener('input', check);
})();

/* ═══════════════════════════════════════════════════════════════
   10. CROP PH SLIDER — sync badge across pages
        (backup in case inline oninput not enough)
═══════════════════════════════════════════════════════════════ */
(function () {
  const sliders = [
    { slider: 'phSlider',  badge: 'phDisplay'  },
    { slider: 'phSliderF', badge: 'phDisplayF' },
  ];
  sliders.forEach(({ slider, badge }) => {
    const sl = document.getElementById(slider);
    const bd = document.getElementById(badge);
    if (sl && bd) {
      sl.addEventListener('input', () => { bd.textContent = sl.value; });
    }
  });
})();

/* ═══════════════════════════════════════════════════════════════
   11. DISEASE IMAGE PREVIEW — drag and drop support
═══════════════════════════════════════════════════════════════ */
(function () {
  const zone  = document.getElementById('uploadZone');
  const input = document.getElementById('leafInput');
  if (!zone || !input) return;

  zone.addEventListener('dragover', e => {
    e.preventDefault();
    zone.style.borderColor = '#2e7d32';
    zone.style.background  = '#e8f5e9';
  });

  zone.addEventListener('dragleave', () => {
    zone.style.borderColor = '#81c784';
    zone.style.background  = '#f8fdf8';
  });

  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.style.borderColor = '#81c784';
    zone.style.background  = '#f8fdf8';
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      input.files = files;
      previewImage(input);
    }
  });
})();

/* ── Global helper (used by disease.html inline) ─────────────── */
function previewImage(input) {
  const preview     = document.getElementById('previewImg');
  const placeholder = document.getElementById('uploadPlaceholder');
  if (!input.files || !input.files[0] || !preview || !placeholder) return;
  const reader = new FileReader();
  reader.onload = e => {
    preview.src = e.target.result;
    preview.classList.remove('d-none');
    placeholder.classList.add('d-none');
  };
  reader.readAsDataURL(input.files[0]);
}

/* ═══════════════════════════════════════════════════════════════
   12. SMOOTH SCROLL TO RESULTS
═══════════════════════════════════════════════════════════════ */
(function () {
  const resultCards = document.querySelectorAll(
    '.result-banner, #marketResult, .forecast-day-card:first-child'
  );
  if (resultCards.length > 0) {
    setTimeout(() => {
      resultCards[0].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 200);
  }
})();
