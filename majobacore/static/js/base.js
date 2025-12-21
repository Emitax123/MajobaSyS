 const hamburger = document.getElementById('hamburger');
        const navMenu = document.querySelector('.nav-menu');

        hamburger.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            
            // Animate hamburger menu
            hamburger.classList.toggle('active');
            const spans = hamburger.querySelectorAll('span');
            
            if (hamburger.classList.contains('active')) {
                spans[0].style.transform = 'rotate(-45deg) translate(-5px, 6px)';
                spans[1].style.opacity = '0';
                spans[2].style.transform = 'rotate(45deg) translate(-5px, -6px)';
            } else {
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            }
        });

        // Close mobile menu when clicking on a link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                hamburger.classList.remove('active');
                const spans = hamburger.querySelectorAll('span');
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
            });
        });

        

        // Dropdown functionality
        document.addEventListener('DOMContentLoaded', function() {

            const mainContent = document.querySelector('.main-content');
            const dropdown = document.querySelector('.dropdown');
            const dropdownToggle = document.querySelector('.dropdown-toggle');
            
            
            if (dropdown && dropdownToggle && !mainContent) {
                // Toggle dropdown when clicking on the toggle
                dropdownToggle.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    dropdown.classList.toggle('active');
                });

                // Close dropdown when clicking outside
                document.addEventListener('click', function(e) {
                    if (!dropdown.contains(e.target)) {
                        dropdown.classList.remove('active');
                    }
                });

                // Close dropdown when clicking on a dropdown link
                const dropdownLinks = dropdown.querySelectorAll('.dropdown-link');
                dropdownLinks.forEach(link => {
                    link.addEventListener('click', function() {
                        dropdown.classList.remove('active');
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