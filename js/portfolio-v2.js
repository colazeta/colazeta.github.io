(() => {
  const body = document.body;
  const current = body.dataset.lang || 'en';
  const map = { en: '/en/', it: '/it/', de: '/de/' };

  const language = document.getElementById('lang-select');
  if (language) {
    language.value = current;
    language.addEventListener('change', (event) => {
      const next = map[event.target.value] || '/en/';
      localStorage.setItem('preferredLang', event.target.value);
      window.location.href = next;
    });
  }

  const toggle = document.querySelector('.menu-toggle');
  const nav = document.getElementById('main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    nav.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  const navLinks = [...document.querySelectorAll('.nav-links a[href^="#"]')];
  const sections = [...document.querySelectorAll('main section[id]')];
  if ('IntersectionObserver' in window && navLinks.length && sections.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        navLinks.forEach((link) => {
          const active = link.getAttribute('href') === `#${entry.target.id}`;
          if (active) link.setAttribute('aria-current', 'true');
          else link.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-24% 0px -62% 0px', threshold: 0 });
    sections.forEach((section) => observer.observe(section));
  }
})();
