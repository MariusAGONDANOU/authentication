// Validation frontend et amélioration UX pour la connexion

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('login-form');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const submitBtn = document.getElementById('submit-btn');
    const submitText = document.getElementById('submit-text');
    const submitLoader = document.getElementById('submit-loader');
    const togglePasswordBtn = document.getElementById('toggle-password');
    const eyeOpen = document.getElementById('eye-open');
    const eyeClosed = document.getElementById('eye-closed');

    // ==================== AFFICHER/MASQUER MOT DE PASSE ====================
    
    if (togglePasswordBtn) {
        togglePasswordBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                eyeOpen.classList.add('hidden');
                eyeClosed.classList.remove('hidden');
            } else {
                passwordInput.type = 'password';
                eyeOpen.classList.remove('hidden');
                eyeClosed.classList.add('hidden');
            }
        });
    }

    // ==================== VALIDATION EN TEMPS RÉEL ====================
    
    // Validation de l'email
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const value = this.value.trim();
            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

            if (value && !emailRegex.test(value)) {
                showFieldError(this, 'Format d\'adresse e-mail invalide');
            } else {
                clearFieldError(this);
            }
        });

        emailInput.addEventListener('input', function() {
            clearFieldError(this);
        });
    }

    // Validation du mot de passe
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            clearFieldError(this);
        });
    }

    // ==================== SOUMISSION DU FORMULAIRE ====================
    
    if (form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;

            // Validation de l'email
            if (emailInput) {
                const email = emailInput.value.trim();
                const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

                if (!email) {
                    showFieldError(emailInput, 'L\'adresse e-mail est obligatoire');
                    isValid = false;
                } else if (!emailRegex.test(email)) {
                    showFieldError(emailInput, 'Format d\'adresse e-mail invalide');
                    isValid = false;
                }
            }

            // Validation du mot de passe
            if (passwordInput) {
                const password = passwordInput.value;

                if (!password) {
                    showFieldError(passwordInput, 'Le mot de passe est obligatoire');
                    isValid = false;
                }
            }

            if (!isValid) {
                e.preventDefault();
                return false;
            }

            // Affichage du loader
            if (submitBtn && !submitBtn.disabled) {
                submitText.classList.add('hidden');
                submitLoader.classList.remove('hidden');
                submitBtn.disabled = true;
                submitBtn.classList.add('cursor-wait', 'opacity-75');
            }
        });
    }

    // ==================== FONCTIONS UTILITAIRES ====================
    
    function showFieldError(input, message) {
        clearFieldError(input);
        
        const errorDiv = document.createElement('p');
        errorDiv.className = 'mt-1 text-sm text-red-600 field-error';
        errorDiv.textContent = message;
        
        const parent = input.parentNode;
        if (parent.classList.contains('relative')) {
            parent.parentNode.appendChild(errorDiv);
        } else {
            parent.appendChild(errorDiv);
        }
        
        input.classList.add('border-red-500', 'focus:ring-red-500');
        input.classList.remove('border-gray-300', 'focus:ring-blue-500');
    }

    function clearFieldError(input) {
        const parent = input.parentNode;
        const errorElement = parent.classList.contains('relative') 
            ? parent.parentNode.querySelector('.field-error')
            : parent.querySelector('.field-error');
        
        if (errorElement) {
            errorElement.remove();
        }
        
        input.classList.remove('border-red-500', 'focus:ring-red-500');
        input.classList.add('border-gray-300', 'focus:ring-blue-500');
    }

    // ==================== AUTO-FOCUS SUR LE PREMIER CHAMP ====================
    
    if (emailInput && !emailInput.value) {
        emailInput.focus();
    }
});
