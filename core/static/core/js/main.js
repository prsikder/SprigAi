// SprigAI shared front-end helpers

document.addEventListener("DOMContentLoaded", function () {
  initHeroHeaderScroll();
  initHeroCarousel();

  // Auto-dismiss alerts after 6s
  document.querySelectorAll(".alert.auto-dismiss").forEach(function (el) {
    setTimeout(function () {
      el.classList.remove("show");
      el.classList.add("fade");
      setTimeout(() => el.remove(), 400);
    }, 6000);
  });

  // Generic image-upload preview: any <input type=file data-preview="#targetId">
  document.querySelectorAll('input[type="file"][data-preview]').forEach(function (input) {
    input.addEventListener("change", function () {
      const targetSel = input.getAttribute("data-preview");
      const target = document.querySelector(targetSel);
      if (!target || !input.files || !input.files[0]) return;
      const file = input.files[0];

      const allowed = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
      if (!allowed.includes(file.type)) {
        target.innerHTML = '<div class="alert alert-danger">Unsupported file type. Please upload JPG, PNG, or WEBP.</div>';
        input.value = "";
        return;
      }
      const maxBytes = (window.SPRIG_MAX_UPLOAD_MB || 8) * 1024 * 1024;
      if (file.size > maxBytes) {
        target.innerHTML = '<div class="alert alert-danger">File is too large. Max size is ' + (window.SPRIG_MAX_UPLOAD_MB || 8) + 'MB.</div>';
        input.value = "";
        return;
      }
      const reader = new FileReader();
      reader.onload = function (e) {
        target.innerHTML = '<img src="' + e.target.result + '" class="img-fluid rounded shadow-sm" style="max-height:320px;">';
      };
      reader.readAsDataURL(file);
    });
  });

  // Submit-button loading state for forms with data-loading-text
  document.querySelectorAll("form[data-loading]").forEach(function (form) {
    form.addEventListener("submit", function () {
      const btn = form.querySelector('button[type="submit"]');
      if (!btn) return;
      btn.disabled = true;
      const original = btn.innerHTML;
      btn.setAttribute("data-original", original);
      btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>' + (form.getAttribute("data-loading") || "Processing...");
    });
  });
});

function initHeroHeaderScroll() {
  var header = document.getElementById("sprigHeader");
  if (!header || !header.classList.contains("sprig-header-hero")) return;

  var scrollThreshold = 48;

  function updateHeaderState() {
    if (window.scrollY > scrollThreshold) {
      header.classList.add("is-scrolled");
    } else {
      header.classList.remove("is-scrolled");
    }
  }

  updateHeaderState();
  window.addEventListener("scroll", updateHeaderState, { passive: true });
}

function initHeroCarousel() {
  var carousel = document.querySelector("[data-hero-carousel]");
  if (!carousel) return;

  var track = carousel.querySelector(".hero-carousel-track");
  var slides = Array.prototype.slice.call(carousel.querySelectorAll(".hero-slide"));
  var indicators = Array.prototype.slice.call(carousel.querySelectorAll(".hero-indicator"));
  if (!track || slides.length === 0) return;

  var current = 0;
  var intervalMs = 3800;
  var transitionMs = 1000;
  var timer = null;
  var isAnimating = false;
  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var edgeRatio = 0.28;

  function resolveDirection(nextIndex, explicitDirection) {
    if (explicitDirection === 1 || explicitDirection === -1) return explicitDirection;
    if (nextIndex === current) return 1;
    if (current === slides.length - 1 && nextIndex === 0) return 1;
    if (current === 0 && nextIndex === slides.length - 1) return -1;
    return nextIndex > current ? 1 : -1;
  }

  function goTo(index, direction) {
    var nextIndex = (index + slides.length) % slides.length;
    if (isAnimating || nextIndex === current) return;

    var dir = resolveDirection(nextIndex, direction);
    isAnimating = true;
    carousel.classList.add("is-sliding");
    carousel.setAttribute("data-direction", dir > 0 ? "forward" : "backward");
    current = nextIndex;

    track.style.transform = "translate3d(-" + (current * 100) + "%, 0, 0)";

    slides.forEach(function (slide, i) {
      slide.classList.toggle("is-active", i === current);
    });

    indicators.forEach(function (indicator, i) {
      indicator.classList.toggle("is-active", i === current);
      indicator.setAttribute("aria-selected", i === current ? "true" : "false");
    });

    window.setTimeout(function () {
      isAnimating = false;
      carousel.classList.remove("is-sliding");
    }, reducedMotion ? 0 : transitionMs);
  }

  function nextSlide() {
    goTo(current + 1, 1);
  }

  function prevSlide() {
    goTo(current - 1, -1);
  }

  function startAutoplay() {
    stopAutoplay();
    if (reducedMotion || slides.length < 2) return;
    timer = window.setInterval(nextSlide, intervalMs);
  }

  function stopAutoplay() {
    if (timer) {
      window.clearInterval(timer);
      timer = null;
    }
  }

  function isInteractiveTarget(target) {
    return !!target.closest(
      "a, button, input, textarea, select, label, .hero-indicator, .hero-panel, .hero-display-title, .hero-cta"
    );
  }

  function zoneFromEvent(event) {
    var rect = carousel.getBoundingClientRect();
    var ratio = (event.clientX - rect.left) / rect.width;
    if (ratio <= edgeRatio) return "prev";
    if (ratio >= 1 - edgeRatio) return "next";
    return null;
  }

  function updateHoverZone(event) {
    if (isInteractiveTarget(event.target)) {
      carousel.classList.remove("is-hover-prev", "is-hover-next");
      return;
    }
    var zone = zoneFromEvent(event);
    carousel.classList.toggle("is-hover-prev", zone === "prev");
    carousel.classList.toggle("is-hover-next", zone === "next");
  }

  carousel.addEventListener("click", function (event) {
    if (isInteractiveTarget(event.target) || isAnimating) return;
    var zone = zoneFromEvent(event);
    if (zone === "prev") {
      prevSlide();
      startAutoplay();
    } else if (zone === "next") {
      nextSlide();
      startAutoplay();
    }
  });

  carousel.addEventListener("mousemove", updateHoverZone);
  carousel.addEventListener("mouseleave", function () {
    carousel.classList.remove("is-hover-prev", "is-hover-next");
  });

  carousel.addEventListener("keydown", function (event) {
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      prevSlide();
      startAutoplay();
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      nextSlide();
      startAutoplay();
    }
  });

  indicators.forEach(function (indicator) {
    indicator.addEventListener("click", function () {
      var target = parseInt(indicator.getAttribute("data-slide-to"), 10);
      if (Number.isNaN(target)) return;
      goTo(target);
      startAutoplay();
    });
  });

  carousel.addEventListener("mouseenter", stopAutoplay);
  carousel.addEventListener("mouseleave", startAutoplay);
  carousel.addEventListener("focusin", stopAutoplay);
  carousel.addEventListener("focusout", startAutoplay);

  carousel.setAttribute("tabindex", "0");

  goTo(0);
  startAutoplay();
}
