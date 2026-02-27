document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.querySelector('.nav-menu');
    const dropdown = document.querySelector('.dropdown');
    const dropdownToggle = document.querySelector('.dropdown-toggle');

    function closeMenu() {
        navMenu.classList.remove('active');
        hamburger.classList.remove('active');
        const spans = hamburger.querySelectorAll('span');
        spans[0].style.transform = 'none';
        spans[1].style.opacity = '1';
        spans[2].style.transform = 'none';
        document.body.style.overflow = '';
    }

    function openMenu() {
        navMenu.classList.add('active');
        hamburger.classList.add('active');
        const spans = hamburger.querySelectorAll('span');
        spans[0].style.transform = 'rotate(-45deg) translate(-5px, 6px)';
        spans[1].style.opacity = '0';
        spans[2].style.transform = 'rotate(45deg) translate(-5px, -6px)';
        document.body.style.overflow = 'hidden';
    }

    // Hamburger menu toggle
    hamburger.addEventListener('click', (e) => {
        e.stopPropagation();
        if (navMenu.classList.contains('active')) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    // Close mobile menu when clicking on a link (except dropdown toggles)
    document.querySelectorAll('.nav-link').forEach(link => {
        if (!link.classList.contains('dropdown-toggle')) {
            link.addEventListener('click', () => {
                closeMenu();
            });
        }
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (navMenu.classList.contains('active') && 
            !navMenu.contains(e.target) && 
            !hamburger.contains(e.target)) {
            closeMenu();
        }
    });

    // Close menu on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && navMenu.classList.contains('active')) {
            closeMenu();
        }
    });

    // Dropdown functionality
    if (dropdown && dropdownToggle) {
        // Toggle dropdown when clicking on the toggle
        dropdownToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            // Si existe la sección "empresas-section" en esta página, hacer scroll en lugar de abrir el dropdown
            const empresasSection = document.getElementById('empresas-section');
            if (empresasSection) {
                const navbarHeight = document.querySelector('.navbar').offsetHeight || 0;
                const offsetPosition = empresasSection.getBoundingClientRect().top + window.pageYOffset - navbarHeight;
                window.scrollTo({ top: offsetPosition, behavior: 'smooth' });
                return; // No abrir el dropdown
            }

            dropdown.classList.toggle('active');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
            }
        });

        // Close dropdown and mobile menu when clicking on a dropdown link
        const dropdownLinks = dropdown.querySelectorAll('.dropdown-link');
        dropdownLinks.forEach(link => {
            link.addEventListener('click', function() {
                dropdown.classList.remove('active');
                closeMenu();
            });
        });

        // Close dropdown when pressing Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && dropdown.classList.contains('active')) {
                dropdown.classList.remove('active');
            }
        });
    }
});