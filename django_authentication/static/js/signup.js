// Validation en temps réel et indicateur de robustesse du mot de passe

document.addEventListener('DOMContentLoaded', function() {
    // Éléments du DOM
    const form = document.getElementById('signup-form');
    const passwordInput = document.getElementById('password');
    const passwordConfirmInput = document.getElementById('password_confirm');
    const acceptTermsCheckbox = document.getElementById('accept_terms');
    const submitBtn = document.getElementById('submit-btn');
    const submitText = document.getElementById('submit-text');
    const submitLoader = document.getElementById('submit-loader');
    
    // Éléments de l'indicateur de robustesse
    const strengthBar = document.getElementById('strength-bar');
    const strengthText = document.getElementById('strength-text');
    const criteriaLength = document.getElementById('criteria-length');
    const criteriaUpper = document.getElementById('criteria-upper');
    const criteriaLower = document.getElementById('criteria-lower');
    const criteriaNumber = document.getElementById('criteria-number');
    const criteriaSpecial = document.getElementById('criteria-special');
    
    // Éléments du sélecteur de pays
    const countrySelectorBtn = document.getElementById('country-selector-btn');
    const countryDropdown = document.getElementById('country-dropdown');
    const selectedCountrySpan = document.getElementById('selected-country');
    const countryCodeInput = document.getElementById('country_code');
    const countrySearch = document.getElementById('country-search');
    const countryOptions = document.querySelectorAll('.country-option');
    
    // Indicateur de correspondance des mots de passe
    const matchIndicator = document.getElementById('match-indicator');
    const matchIcon = document.getElementById('match-icon');

    // ==================== GESTION DU SÉLECTEUR DE PAYS ====================
    
    // Ouvrir/fermer le dropdown
    countrySelectorBtn.addEventListener('click', function(e) {
        e.preventDefault();
        countryDropdown.classList.toggle('hidden');
        countrySearch.value = '';
        filterCountries('');
    });

    // Fermer le dropdown si clic à l'extérieur
    document.addEventListener('click', function(e) {
        if (!countrySelectorBtn.contains(e.target) && !countryDropdown.contains(e.target)) {
            countryDropdown.classList.add('hidden');
        }
    });

    // Recherche de pays
    countrySearch.addEventListener('input', function() {
        filterCountries(this.value.toLowerCase());
    });

    function filterCountries(searchTerm) {
        countryOptions.forEach(option => {
            const countryName = option.textContent.toLowerCase();
            if (countryName.includes(searchTerm)) {
                option.style.display = 'flex';
            } else {
                option.style.display = 'none';
            }
        });
    }

    // Sélection d'un pays
    countryOptions.forEach(option => {
        option.addEventListener('click', function() {
            const code = this.getAttribute('data-code');
            const flag = this.getAttribute('data-flag');
            
            selectedCountrySpan.innerHTML = '<span class="mr-1">' + flag + '</span><span>' + code + '</span>';
            countryCodeInput.value = code;
            countryDropdown.classList.add('hidden');
        });
    });

    // ==================== VALIDATION DU MOT DE PASSE ====================
    
    function checkPasswordStrength(password) {
        let strength = 0;
        const criteria = {
            length: password.length >= 8,
            upper: /[A-Z]/.test(password),
            lower: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        // Mise à jour des indicateurs visuels
        updateCriterion(criteriaLength, criteria.length);
        updateCriterion(criteriaUpper, criteria.upper);
        updateCriterion(criteriaLower, criteria.lower);
        updateCriterion(criteriaNumber, criteria.number);
        updateCriterion(criteriaSpecial, criteria.special);

        // Calcul de la force
        Object.values(criteria).forEach(function(met) {
            if (met) strength++;
        });

        // Bonus pour longueur supplémentaire
        if (password.length >= 12) strength += 0.5;
        if (password.length >= 16) strength += 0.5;

        return {
            score: strength,
            criteria: criteria
        };
    }

    function updateCriterion(element, met) {
        if (met) {
            element.textContent = '✓';
            element.className = 'text-green-500 font-bold';
        } else {
            element.textContent = '○';
            element.className = 'text-gray-400';
        }
    }

    function updateStrengthIndicator(strength) {
        const colors = {
            0: { color: 'bg-gray-300', width: '0%', text: '-', textColor: 'text-gray-500' },
            1: { color: 'bg-red-500', width: '20%', text: 'Très faible', textColor: 'text-red-500' },
            2: { color: 'bg-orange-500', width: '40%', text: 'Faible', textColor: 'text-orange-500' },
            3: { color: 'bg-yellow-500', width: '60%', text: 'Moyen', textColor: 'text-yellow-600' },
            4: { color: 'bg-lime-500', width: '80%', text: 'Fort', textColor: 'text-lime-600' },
            5: { color: 'bg-green-500', width: '100%', text: 'Très fort', textColor: 'text-green-600' },
            6: { color: 'bg-green-600', width: '100%', text: 'Robuste', textColor: 'text-green-700' }
        };

        const level = Math.min(Math.floor(strength), 6);
        const config = colors[level];

        strengthBar.className = 'password-strength-bar h-full rounded-full ' + config.color;
        strengthBar.style.width = config.width;
        strengthText.textContent = config.text;
        strengthText.className = 'text-xs font-medium ' + config.textColor;
    }

    passwordInput.addEventListener('input', function() {
        const password = this.value;
        
        if (password.length === 0) {
            updateStrengthIndicator(0);
            return;
        }

        const result = checkPasswordStrength(password);
        updateStrengthIndicator(result.score);
        
        // Vérifier la correspondance si le champ de confirmation n'est pas vide
        checkPasswordMatch();
    });

    // ==================== VALIDATION DE LA CONFIRMATION ====================
    
    function checkPasswordMatch() {
        const password = passwordInput.value;
        const passwordConfirm = passwordConfirmInput.value;

        if (passwordConfirm.length === 0) {
            matchIndicator.classList.add('hidden');
            return;
        }

        matchIndicator.classList.remove('hidden');

        if (password === passwordConfirm) {
            matchIcon.textContent = '✓';
            matchIcon.className = 'text-green-500 text-xl font-bold';
        } else {
            matchIcon.textContent = '✗';
            matchIcon.className = 'text-red-500 text-xl font-bold';
        }
    }

    passwordConfirmInput.addEventListener('input', checkPasswordMatch);

    // ==================== ACTIVATION DU BOUTON ====================
    
    function updateSubmitButton() {
        if (acceptTermsCheckbox.checked) {
            submitBtn.disabled = false;
            submitBtn.classList.remove('bg-gray-400', 'cursor-not-allowed', 'opacity-50');
            submitBtn.classList.add('bg-blue-600', 'hover:bg-blue-700', 'cursor-pointer', 'shadow-lg', 'hover:shadow-xl', 'transform', 'hover:-translate-y-0.5');
        } else {
            submitBtn.disabled = true;
            submitBtn.classList.add('bg-gray-400', 'cursor-not-allowed', 'opacity-50');
            submitBtn.classList.remove('bg-blue-600', 'hover:bg-blue-700', 'cursor-pointer', 'shadow-lg', 'hover:shadow-xl', 'transform', 'hover:-translate-y-0.5');
        }
    }

    acceptTermsCheckbox.addEventListener('change', updateSubmitButton);

    // ==================== SOUMISSION DU FORMULAIRE ====================
    
    form.addEventListener('submit', function() {
        if (!submitBtn.disabled) {
            submitText.classList.add('hidden');
            submitLoader.classList.remove('hidden');
            submitBtn.disabled = true;
            submitBtn.classList.add('cursor-wait');
        }
    });

    // ==================== VALIDATION EN TEMPS RÉEL DES AUTRES CHAMPS ====================
    
    const fullNameInput = document.getElementById('full_name');
    const emailInput = document.getElementById('email');

    // Validation du nom complet
    if (fullNameInput) {
        fullNameInput.addEventListener('blur', function() {
            const value = this.value.trim();
            const patterns = [
                /^[A-Za-zÀ-ÿ]+[\s_][A-Za-zÀ-ÿ]+[\s_]*[A-Za-zÀ-ÿ]*$/,
                /^[A-Z][a-z]+[A-Z][a-z]+[A-Z]*[a-z]*$/
            ];

            let isValid = false;
            for (let i = 0; i < patterns.length; i++) {
                if (patterns[i].test(value)) {
                    const segments = value.split(/[\s_]|(?=[A-Z])/).filter(function(s) { return s; });
                    if (segments.length >= 2) {
                        isValid = true;
                        break;
                    }
                }
            }

            if (value && !isValid) {
                showFieldError(this, 'Format invalide. Utilisez: "Nom Prénom", "Nom_Prénom" ou "NomPrénom"');
            } else {
                clearFieldError(this);
            }
        });
    }

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
    }

    function showFieldError(input, message) {
        clearFieldError(input);
        
        const errorDiv = document.createElement('p');
        errorDiv.className = 'mt-1 text-sm text-red-600 field-error';
        errorDiv.textContent = message;
        
        input.parentNode.appendChild(errorDiv);
        input.classList.add('border-red-500', 'focus:ring-red-500');
        input.classList.remove('border-gray-300', 'focus:ring-blue-500');
    }

    function clearFieldError(input) {
        const existingError = input.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        
        input.classList.remove('border-red-500', 'focus:ring-red-500');
        input.classList.add('border-gray-300', 'focus:ring-blue-500');
    }

    // Initialisation
    updateSubmitButton();
});


