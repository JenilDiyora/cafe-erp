/**
 * Artisan Brew Cafe — Main Client-side Script
 * Phase 1 Django + Jinja2 Traditional Server Rendered Website
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Sticky Navbar shadow on scroll
  const navbar = document.querySelector('.cafe-navbar');
  if (navbar) {
    const handleScroll = () => {
      if (window.scrollY > 30) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
  }

  // 2. Gallery Lightbox Functionality
  const galleryCards = document.querySelectorAll('.gallery-card');
  const lightboxModalEl = document.getElementById('galleryLightboxModal');
  if (lightboxModalEl && galleryCards.length > 0) {
    const lightboxModal = new bootstrap.Modal(lightboxModalEl);
    const lightboxImg = lightboxModalEl.querySelector('#lightboxImage');
    const lightboxTitle = lightboxModalEl.querySelector('#lightboxTitle');
    const lightboxCaption = lightboxModalEl.querySelector('#lightboxCaption');

    galleryCards.forEach(card => {
      card.addEventListener('click', () => {
        const fullSrc = card.getAttribute('data-full-src');
        const title = card.getAttribute('data-title');
        const caption = card.getAttribute('data-caption');

        if (lightboxImg) lightboxImg.src = fullSrc || '';
        if (lightboxTitle) lightboxTitle.textContent = title || '';
        if (lightboxCaption) lightboxCaption.textContent = caption || '';

        lightboxModal.show();
      });
    });
  }

  // 3. Auto-dismiss alerts after 5 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 6000);
  });

  // 4. Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href && href !== '#' && href.startsWith('#')) {
        const targetEl = document.querySelector(href);
        if (targetEl) {
          e.preventDefault();
          targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  });

  // 5. Contact Form submission feedback
  const contactForm = document.getElementById('contactInquiryForm');
  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      const submitBtn = contactForm.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Sending...';
      }
    });
  }

  // 6. Theme Toggle (Dark / Light Mode)
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  if (themeToggleBtn) {
    const updateToggleIcon = (theme) => {
      const icon = themeToggleBtn.querySelector('i');
      if (icon) {
        if (theme === 'dark') {
          icon.className = 'bi bi-sun-fill text-warning';
          themeToggleBtn.setAttribute('title', 'Switch to light mode');
          themeToggleBtn.classList.remove('btn-outline-secondary');
          themeToggleBtn.classList.add('btn-outline-warning');
        } else {
          icon.className = 'bi bi-moon-stars-fill text-dark';
          themeToggleBtn.setAttribute('title', 'Switch to dark mode');
          themeToggleBtn.classList.remove('btn-outline-warning');
          themeToggleBtn.classList.add('btn-outline-secondary');
        }
      }
    };

    const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
    updateToggleIcon(currentTheme);

    themeToggleBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-bs-theme') || 'light';
      const nextTheme = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-bs-theme', nextTheme);
      try {
        localStorage.setItem('mitra-theme', nextTheme);
      } catch (e) {}
      updateToggleIcon(nextTheme);
      window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: nextTheme } }));
    });
  }

  // 7. Interactive Cafe Maps (MapLibre GL + OpenFreeMap: Clean Vector Maps, Zero Watermarks, Native Dark & Bright)
  const mapContainers = document.querySelectorAll('.cafe-interactive-map, .cafe-leaflet-map');
  if (mapContainers.length > 0 && typeof maplibregl !== 'undefined') {
    const maps = [];
    const lightStyle = 'https://tiles.openfreemap.org/styles/bright';
    const darkStyle = 'https://tiles.openfreemap.org/styles/dark';

    mapContainers.forEach(container => {
      const lat = parseFloat(container.getAttribute('data-lat')) || 21.266236;
      const lng = parseFloat(container.getAttribute('data-lng')) || 72.823239;
      const zoom = parseFloat(container.getAttribute('data-zoom')) || 15.5;
      const mapsUrl = container.getAttribute('data-maps-url') || 'https://maps.app.goo.gl/YjiYuT8wt5XhwfJC7';
      const address = container.getAttribute('data-address') || 'Mitra Cafe, Chhaprabhatha, Surat, Gujarat 394520';

      const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
      const initialStyle = currentTheme === 'dark' ? darkStyle : lightStyle;

      const map = new maplibregl.Map({
        container: container,
        style: initialStyle,
        center: [lng, lat],
        zoom: zoom,
        scrollZoom: false
      });

      // Navigation controls (+ / - buttons)
      map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');

      // Custom pulsing gold coffee pin
      const pinEl = document.createElement('div');
      pinEl.className = 'custom-cafe-pin';
      pinEl.innerHTML = `
        <div class="cafe-pin-pulse"></div>
        <div class="cafe-pin-icon" title="Mitra Cafe">
          <i class="bi bi-cup-hot-fill"></i>
        </div>
      `;

      const popup = new maplibregl.Popup({
        offset: 25,
        closeButton: true,
        focusAfterOpen: false
      }).setHTML(`
        <div class="p-1 text-center" style="min-width: 200px;">
          <h6 class="fw-bold mb-1" style="color: var(--secondary-color);">☕ Mitra Cafe</h6>
          <p class="small mb-2 text-muted" style="line-height: 1.4;">${address}</p>
          <a href="${mapsUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-cafe-primary w-100 py-1" style="font-size: 0.8rem;">
            <i class="bi bi-geo-alt-fill me-1"></i> Open in Google Maps
          </a>
        </div>
      `);

      const marker = new maplibregl.Marker({ element: pinEl })
        .setLngLat([lng, lat])
        .setPopup(popup)
        .addTo(map);

      maps.push({ map, marker, pinEl });
    });

    // Theme toggle listener: seamlessly update vector style between Dark and Bright
    window.addEventListener('themeChanged', (e) => {
      const isDark = e.detail.theme === 'dark';
      const targetStyle = isDark ? darkStyle : lightStyle;
      maps.forEach(item => {
        item.map.setStyle(targetStyle);
      });
    });

    // Responsive resize handler
    window.addEventListener('resize', () => {
      maps.forEach(item => item.map.resize());
    });
  }
});

