document.addEventListener('DOMContentLoaded', function() {
    // Navbar scroll effect
    const header = document.querySelector('header');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - header.offsetHeight,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Form validation for contact form
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Get form fields
            const nameField = document.getElementById('nome');
            const emailField = document.getElementById('email');
            const messageField = document.getElementById('mensagem');
            
            // Reset error states
            removeErrorState(nameField);
            removeErrorState(emailField);
            removeErrorState(messageField);
            
            // Validate name
            if (!nameField.value.trim()) {
                setErrorState(nameField, 'Por favor, informe seu nome');
                isValid = false;
            }
            
            // Validate email
            if (!emailField.value.trim()) {
                setErrorState(emailField, 'Por favor, informe seu email');
                isValid = false;
            } else if (!isValidEmail(emailField.value)) {
                setErrorState(emailField, 'Por favor, informe um email válido');
                isValid = false;
            }
            
            // Validate message
            if (!messageField.value.trim()) {
                setErrorState(messageField, 'Por favor, escreva sua mensagem');
                isValid = false;
            }
            
            // Prevent form submission if invalid
            if (!isValid) {
                e.preventDefault();
            } else {
                // Show success message (in production, this would be handled by backend)
                const formContainer = document.querySelector('.form-container');
                const successMsg = document.createElement('div');
                successMsg.className = 'alert alert-success';
                successMsg.innerHTML = 'Mensagem enviada com sucesso! Entraremos em contato em breve.';
                
                contactForm.style.display = 'none';
                formContainer.appendChild(successMsg);
                
                e.preventDefault(); // Prevent actual submission in this demo
            }
        });
    }

    // Form validation for waitlist form
    const waitlistForm = document.getElementById('waitlistForm');
    if (waitlistForm) {
        waitlistForm.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Get form fields
            const nameField = document.getElementById('waitlist-nome');
            const emailField = document.getElementById('waitlist-email');
            
            // Reset error states
            removeErrorState(nameField);
            removeErrorState(emailField);
            
            // Validate name
            if (!nameField.value.trim()) {
                setErrorState(nameField, 'Por favor, informe seu nome');
                isValid = false;
            }
            
            // Validate email
            if (!emailField.value.trim()) {
                setErrorState(emailField, 'Por favor, informe seu email');
                isValid = false;
            } else if (!isValidEmail(emailField.value)) {
                setErrorState(emailField, 'Por favor, informe um email válido');
                isValid = false;
            }
            
            // Prevent form submission if invalid
            if (!isValid) {
                e.preventDefault();
            } else {
                // Show success message
                const formContainer = document.querySelector('.waitlist-form');
                const successMsg = document.createElement('div');
                successMsg.className = 'alert alert-success mt-3';
                successMsg.innerHTML = 'Inscrição realizada com sucesso! Você receberá nossas ofertas exclusivas.';
                
                waitlistForm.style.display = 'none';
                formContainer.appendChild(successMsg);
                
                e.preventDefault(); // Prevent actual submission in this demo
            }
        });
    }

    // Helper functions for form validation
    function setErrorState(element, message) {
        element.classList.add('is-invalid');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        element.parentNode.appendChild(errorDiv);
    }
    
    function removeErrorState(element) {
        element.classList.remove('is-invalid');
        
        const errorMessage = element.parentNode.querySelector('.invalid-feedback');
        if (errorMessage) {
            errorMessage.remove();
        }
    }
    
    function isValidEmail(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }

    // Animation on scroll
    const animatedElements = document.querySelectorAll('.animated');
    
    function checkIfInView() {
        animatedElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementTop < windowHeight - 100) {
                element.classList.add('fadeIn');
            }
        });
    }
    
    // Check on load
    checkIfInView();
    
    // Check on scroll
    window.addEventListener('scroll', checkIfInView);

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
