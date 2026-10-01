/* =========================================================================
   PORTFOLIO INTERACTIVE SCRIPTS
   ========================================================================= */

document.addEventListener('DOMContentLoaded', () => {
  // --- Header Scroll Effect ---
  const header = document.querySelector('.header');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  });

  // --- Dynamic Typing Effect ---
  const words = [
    'Robotics Software Engineer',
    'Autonomous Systems Developer',
    'ROS & ROS2 Specialist',
    'Mechatronics Engineer'
  ];
  let wordIndex = 0;
  let charIndex = 0;
  let isDeleting = false;
  const typingTextSpan = document.getElementById('typing-text');
  const typingSpeed = 100;
  const erasingSpeed = 50;
  const delayBetweenWords = 2000;

  function typeEffect() {
    const currentWord = words[wordIndex];
    if (isDeleting) {
      typingTextSpan.textContent = currentWord.substring(0, charIndex - 1);
      charIndex--;
    } else {
      typingTextSpan.textContent = currentWord.substring(0, charIndex + 1);
      charIndex++;
    }

    let currentSpeed = isDeleting ? erasingSpeed : typingSpeed;

    if (!isDeleting && charIndex === currentWord.length) {
      currentSpeed = delayBetweenWords;
      isDeleting = true;
    } else if (isDeleting && charIndex === 0) {
      isDeleting = false;
      wordIndex = (wordIndex + 1) % words.length;
      currentSpeed = 500;
    }

    setTimeout(typeEffect, currentSpeed);
  }

  if (typingTextSpan) {
    typeEffect();
  }

  // --- Scroll Animations (Fade In Sections) ---
  const faders = document.querySelectorAll('.fade-in-section');
  const appearOptions = {
    threshold: 0.15,
    rootMargin: "0px 0px -50px 0px"
  };

  const appearOnScroll = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    });
  }, appearOptions);

  faders.forEach(fader => {
    appearOnScroll.observe(fader);
  });

  // --- Active Nav Link Highlight ---
  const sections = document.querySelectorAll('section');
  const navLinks = document.querySelectorAll('.nav-link');

  window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.clientHeight;
      if (window.scrollY >= (sectionTop - 200)) {
        current = section.getAttribute('id');
      }
    });

    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href').slice(1) === current) {
        link.classList.add('active');
      }
    });
  });

  // --- Interactive Project Filtering ---
  const filterButtons = document.querySelectorAll('.filter-btn');
  const projectCards = document.querySelectorAll('.project-card');

  filterButtons.forEach(button => {
    button.addEventListener('click', () => {
      // Toggle active class on buttons
      filterButtons.forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');

      const filterValue = button.getAttribute('data-filter');

      projectCards.forEach(card => {
        const projectTags = card.getAttribute('data-tags').split(' ');
        
        if (filterValue === 'all' || projectTags.includes(filterValue)) {
          card.style.display = 'flex';
          setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'scale(1)';
          }, 50);
        } else {
          card.style.opacity = '0';
          card.style.transform = 'scale(0.9)';
          setTimeout(() => {
            card.style.display = 'none';
          }, 300);
        }
      });
    });
  });

  // --- Contact Form Submission & Validation ---
  const contactForm = document.getElementById('contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();

      const name = document.getElementById('form-name').value.trim();
      const email = document.getElementById('form-email').value.trim();
      const subject = document.getElementById('form-subject').value.trim();
      const message = document.getElementById('form-message').value.trim();

      if (!name || !email || !subject || !message) {
        alert('Please fill out all fields.');
        return;
      }

      // Format email body and trigger client mailto
      const mailtoLink = `mailto:nakhyeshrikar@icloud.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(`Hi Shrikar,\n\nMy name is ${name} (${email}).\n\n${message}`)}`;
      window.location.href = mailtoLink;
      
      contactForm.reset();
    });
  }
});
