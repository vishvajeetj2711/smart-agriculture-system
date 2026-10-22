/**
 * Smart Agriculture — Language Toggle System
 * Switches the entire page between English and Gujarati
 * using data-en / data-gu attributes on elements.
 * Language choice is stored in localStorage so it persists across pages.
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'agri_lang';       // 'en' or 'gu'
  const DEFAULT     = 'gu';              // default language

  /* ── Get current language ──────────────────────────────────── */
  function getLang() {
    return localStorage.getItem(STORAGE_KEY) || DEFAULT;
  }

  /* ── Apply language to the entire document ─────────────────── */
  function applyLang(lang) {
    // Update all elements that carry data-en / data-gu
    document.querySelectorAll('[data-en]').forEach(el => {
      const txt = el.getAttribute('data-' + lang);
      if (txt !== null) el.textContent = txt;
    });

    // Update placeholder attributes
    document.querySelectorAll('[data-ph-en]').forEach(el => {
      const ph = el.getAttribute('data-ph-' + lang);
      if (ph !== null) el.placeholder = ph;
    });

    // Show/hide language-specific blocks
    document.querySelectorAll('.lang-en').forEach(el => {
      el.style.display = lang === 'en' ? '' : 'none';
    });
    document.querySelectorAll('.lang-gu').forEach(el => {
      el.style.display = lang === 'gu' ? '' : 'none';
    });

    // Update the toggle button appearance
    const btn = document.getElementById('langToggleBtn');
    if (btn) {
      if (lang === 'gu') {
        btn.innerHTML = '<span class="flag-icon">🇬🇧</span> English';
        btn.title     = 'Switch to English';
      } else {
        btn.innerHTML = '<span class="flag-icon">🇮🇳</span> ગુજρатی';
        btn.title     = 'ગुजρатीमां बदλο';
      }
    }

    // Update <html lang=""> attribute
    document.documentElement.lang = lang === 'gu' ? 'gu' : 'en';

    // Store choice
    localStorage.setItem(STORAGE_KEY, lang);
  }

  /* ── Toggle handler ────────────────────────────────────────── */
  window.toggleLanguage = function () {
    const next = getLang() === 'gu' ? 'en' : 'gu';
    applyLang(next);

    // Small animation flash on body
    document.body.style.transition = 'opacity 0.15s';
    document.body.style.opacity    = '0.7';
    setTimeout(() => { document.body.style.opacity = '1'; }, 150);
  };

  /* ── On DOM ready: apply saved language ────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    applyLang(getLang());
  });

})();
