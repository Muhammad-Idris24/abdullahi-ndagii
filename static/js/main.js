/* ================================================================
   Abdullahi Ndagi Adamu — Portfolio
   Main JavaScript: intro animation, navigation, scroll effects
   ================================================================ */
(function () {
  'use strict';

  var doc = document;
  var root = doc.documentElement;
  var body = doc.body;
  var INTRO_KEY = 'ana_intro_seen_v1';

  // ----- Helpers -----
  function $(sel, ctx) { return (ctx || doc).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); }

  function shouldPlayIntro() {
    // Play intro on first visit or when coming from external source (e.g. social media).
    try {
      var fromExternal = doc.referrer && doc.referrer.indexOf(location.hostname) === -1;
      var hasSeen = sessionStorage.getItem(INTRO_KEY) === '1';
      // Always play when arriving from an external link, OR on the very first session visit.
      return fromExternal || !hasSeen;
    } catch (e) {
      return true;
    }
  }
  function markIntroSeen() {
    try { sessionStorage.setItem(INTRO_KEY, '1'); } catch (e) {}
  }

  // ----- Intro overlay -----
  function initIntro() {
    var overlay = $('#intro-overlay');
    if (!overlay) return;

    if (!body.hasAttribute('data-intro') || !shouldPlayIntro()) {
      overlay.setAttribute('aria-hidden', 'true');
      overlay.style.display = 'none';
      return;
    }

    body.classList.add('is-intro');
    overlay.setAttribute('aria-hidden', 'false');

    // Dismiss on scroll, click, or after a duration
    function dismiss() {
      dismiss = function () {}; // run once
      overlay.classList.add('is-gone');
      body.classList.remove('is-intro');
      markIntroSeen();
      setTimeout(function () {
        overlay.style.display = 'none';
      }, 700);
    }

    var autoDelay = 3200;
    setTimeout(dismiss, autoDelay);
    doc.addEventListener('click', dismiss, { once: true, passive: true });
    doc.addEventListener('keydown', function onKey(e) {
      if (e.key === 'Escape' || e.key === ' ' || e.key === 'Enter') {
        doc.removeEventListener('keydown', onKey);
        dismiss();
      }
    });
    doc.addEventListener('touchstart', dismiss, { once: true, passive: true });
    doc.addEventListener('wheel', dismiss, { once: true, passive: true });
  }

  // ----- Mobile navigation -----
  function initNav() {
    var toggle = $('.nav-toggle');
    var nav = $('#primary-nav');
    if (!toggle || !nav) return;

    function setOpen(open) {
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      nav.classList.toggle('is-open', !!open);
      toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    }

    toggle.addEventListener('click', function () {
      var isOpen = toggle.getAttribute('aria-expanded') === 'true';
      setOpen(!isOpen);
    });

    // Close after click on a link
    $$('a', nav).forEach(function (a) {
      a.addEventListener('click', function () { setOpen(false); });
    });

    // Close on escape
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') setOpen(false);
    });
  }

  // ----- Header scrolled state -----
  function initHeaderScroll() {
    var header = $('.site-header');
    if (!header) return;
    var ticking = false;

    function update() {
      if (window.scrollY > 4) header.classList.add('is-scrolled');
      else header.classList.remove('is-scrolled');
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) {
        requestAnimationFrame(update);
        ticking = true;
      }
    }, { passive: true });
    update();
  }

  // ----- Smooth in-view reveal (tasteful, minimal) -----
  function initReveal() {
    if (typeof IntersectionObserver === 'undefined') return;
    var targets = $$('.work-card, .project-card, .exhibition-item, .cv-block, .download-card, .section-head, .artwork-section, .project-section');
    if (!targets.length) return;

    targets.forEach(function (el) { el.style.opacity = '0'; el.style.transform = 'translateY(12px)'; el.style.transition = 'opacity .7s ease, transform .7s ease'; });

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var el = entry.target;
          el.style.opacity = '';
          el.style.transform = '';
          io.unobserve(el);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

    targets.forEach(function (el) { io.observe(el); });
  }

  // ----- Boot -----
  function boot() {
    initIntro();
    initNav();
    initHeaderScroll();
    try { initReveal(); } catch (e) {}
  }

  if (doc.readyState === 'loading') {
    doc.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
