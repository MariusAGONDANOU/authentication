// Gestion de la modale de profil et des mises à jour AJAX

document.addEventListener('DOMContentLoaded', function() {
    // ==================== ÉLÉMENTS DU DOM ====================
    
    // Modale
    const profileModal = document.getElementById('profile-modal');
    const editProfileBtn = document.getElementById('edit-profile-btn');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const cancelModalBtn = document.getElementById('cancel-modal-btn');
    
    // Vérification que les éléments existent
    if (!profileModal || !editProfileBtn) {
        console.warn('Profile modal elements not found');
        return;
    }
    
    // Fonction utilitaire pour accéder en toute sécurité aux propriétés des éléments
    function safeClassList(element, action, className) {
        if (!element || !element.classList) return;
        if (action === 'add' && className) {
            element.classList.add(className);
        } else if (action === 'remove' && className) {
            element.classList.remove(className);
        } else if (action === 'toggle' && className) {
            element.classList.toggle(className);
        }
    }
    
    // Formulaire
    const profileForm = document.getElementById('profile-form');
    const saveProfileBtn = document.getElementById('save-profile-btn');
    const saveText = document.getElementById('save-text');
    const saveLoader = document.getElementById('save-loader');
    
    // Champs du formulaire
    const fullNameInput = document.getElementById('modal-full-name');
    const emailInput = document.getElementById('modal-email');
    const phoneInput = document.getElementById('modal-phone');
    const profilePictureInput = document.getElementById('profile-picture-input');
    const uploadPhotoBtn = document.getElementById('upload-photo-btn');
    const deletePhotoBtn = document.getElementById('delete-photo-btn');
    
    // Prévisualisations
    let modalAvatarPreviewImg = document.getElementById('modal-avatar-preview-img');
    const modalAvatarPreviewInitials = document.getElementById('modal-avatar-preview-initials');
    const sidebarAvatarImg = document.getElementById('sidebar-avatar-img');
    const sidebarAvatarInitials = document.getElementById('sidebar-avatar-initials');
    const sidebarUserName = document.getElementById('sidebar-user-name');
    
    // Toast
    const toastNotification = document.getElementById('toast-notification');
    const toastMessage = document.getElementById('toast-message');
    const toastIcon = document.getElementById('toast-icon');
    const closeToastBtn = document.getElementById('close-toast-btn');
    
    // Variable pour stocker le fichier sélectionné
    let selectedFile = null;
    let deletePhoto = false;

    // ==================== GESTION DE LA MODALE ====================
    
    // Ouvrir la modale
    if (editProfileBtn) {
        editProfileBtn.addEventListener('click', function() {
            profileModal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
            
            // Réinitialise les erreurs
            clearAllErrors();
        });
    }
    
    // Fermer la modale
    function closeModal() {
        profileModal.classList.add('hidden');
        document.body.style.overflow = 'auto';
        selectedFile = null;
        deletePhoto = false;
    }
    
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }
    
    if (cancelModalBtn) {
        cancelModalBtn.addEventListener('click', closeModal);
    }
    
    // Fermer au clic sur le fond
    profileModal.addEventListener('click', function(e) {
        if (e.target === profileModal) {
            closeModal();
        }
    });
    
    // Fermer avec Échap
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !profileModal.classList.contains('hidden')) {
            closeModal();
        }
    });

    // ==================== UPLOAD DE PHOTO ====================
    
    if (uploadPhotoBtn) {
        uploadPhotoBtn.addEventListener('click', function() {
            profilePictureInput.click();
        });
    }
    
    if (profilePictureInput) {
        profilePictureInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            
            if (file) {
                // Validation de la taille (5MB max)
                if (file.size > 5 * 1024 * 1024) {
                    showToast('La taille de l\'image ne doit pas dépasser 5MB', 'error');
                    profilePictureInput.value = '';
                    return;
                }
                
                // Validation du type
                const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif', 'image/webp'];
                if (!validTypes.includes(file.type)) {
                    showToast('Format non supporté. Utilisez JPG, PNG, GIF ou WEBP', 'error');
                    profilePictureInput.value = '';
                    return;
                }
                
                // Prévisualisation
                const reader = new FileReader();
                reader.onload = function(e) {
                    try {
                        // Mettre à jour les références aux éléments
                        modalAvatarPreviewImg = document.getElementById('modal-avatar-preview-img');
                        const previewInitials = document.getElementById('modal-avatar-preview-initials');
                        
                        // Mettre à jour l'image de prévisualisation
                        if (modalAvatarPreviewImg) {
                            modalAvatarPreviewImg.src = e.target.result;
                            safeClassList(modalAvatarPreviewImg, 'remove', 'hidden');
                        }
                        
                        // Masquer les initiales
                        if (previewInitials) {
                            safeClassList(previewInitials, 'add', 'hidden');
                        }
                        
                        // Mettre à jour le texte du bouton
                        if (uploadPhotoBtn) {
                            uploadPhotoBtn.innerHTML = `
                                <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                </svg>
                                Changer la photo
                            `;
                        }
                        
                        // Afficher le bouton de suppression
                        if (deletePhotoBtn) safeClassList(deletePhotoBtn, 'remove', 'hidden');
                    } catch (error) {
                        console.error('Erreur lors de la prévisualisation de l\'image :', error);
                    }
                };
                reader.readAsDataURL(file);
                
                selectedFile = file;
                deletePhoto = false;
            }
        });
    }

    // ==================== SUPPRESSION DE PHOTO ====================
    
    if (deletePhotoBtn) {
        deletePhotoBtn.addEventListener('click', function() {
            if (confirm('Êtes-vous sûr de vouloir supprimer votre photo de profil ?')) {
                deletePhoto = true;
                selectedFile = null;
                if (profilePictureInput) profilePictureInput.value = '';
                
                // Affiche les initiales et masque l'image
                if (modalAvatarPreviewImg) safeClassList(modalAvatarPreviewImg, 'add', 'hidden');
                if (modalAvatarPreviewInitials) safeClassList(modalAvatarPreviewInitials, 'remove', 'hidden');
                
                // Mettre à jour le texte du bouton
                if (uploadPhotoBtn) {
                    uploadPhotoBtn.innerHTML = `
                        <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                        Définir la photo
                    `;
                }
                
                // Masquer le bouton de suppression
                if (deletePhotoBtn) safeClassList(deletePhotoBtn, 'add', 'hidden');
                
                // Ne pas appeler l'API ici, on attend la soumission du formulaire
            }
        });
    }
    
    function deleteProfilePicture() {
        fetch('/api/profile/delete-picture/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Met à jour la sidebar
                if (sidebarAvatarImg) {
                    sidebarAvatarImg.remove();
                }
                
                if (sidebarAvatarInitials) {
                    sidebarAvatarInitials.classList.remove('hidden');
                    sidebarAvatarInitials.textContent = data.data.initials;
                } else {
                    // Crée l'élément initiales si n'existe pas
                    const initialsDiv = document.createElement('div');
                    initialsDiv.id = 'sidebar-avatar-initials';
                    initialsDiv.className = 'w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold text-lg ring-2 ring-gray-200 transition-all group-hover:ring-blue-500';
                    initialsDiv.textContent = data.data.initials;
                    
                    const avatarContainer = document.querySelector('.sidebar-component .relative.group');
                    if (avatarContainer) {
                        avatarContainer.insertBefore(initialsDiv, avatarContainer.firstChild);
                    }
                }
                
                // Cache le bouton supprimer
                if (deletePhotoBtn) {
                    deletePhotoBtn.classList.add('hidden');
                }
                
                showToast(data.message, 'success');
            } else {
                showToast(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            showToast('Erreur lors de la suppression', 'error');
        });
    }

    // ==================== VALIDATION EN TEMPS RÉEL ====================
    
    if (fullNameInput) {
        fullNameInput.addEventListener('blur', function() {
            validateFullName(this.value);
        });
        
        fullNameInput.addEventListener('input', function() {
            clearError('full_name');
        });
    }
    
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            validateEmail(this.value);
        });
    }
    
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            clearError('phone');
        });
    }
    
    function validateFullName(name) {
        // Vérifie si le champ est vide
        if (!name || !name.trim()) {
            showError('full_name', 'Le nom complet est requis');
            return false;
        }
        
        // Vérifie la longueur minimale
        if (name.trim().length < 2) {
            showError('full_name', 'Le nom complet doit contenir au moins 2 caractères');
            return false;
        }
        
        // Vérifie le format du nom (plus permissif pour les caractères internationaux)
        const nameRegex = /^[\p{L}\s'-]+$/u;
        if (!nameRegex.test(name.trim())) {
            showError('full_name', 'Le nom contient des caractères non autorisés');
            return false;
        }
        
        // Si on arrive ici, la validation est réussie
        clearError('full_name');
        return true;
    }
    
    function validateEmail(email) {
        // Vérifie si le champ est vide
        if (!email || !email.trim()) {
            showError('email', 'L\'adresse e-mail est requise');
            return false;
        }
        
        // Expression régulière plus permissive pour l'email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!emailRegex.test(email.trim())) {
            showError('email', 'Veuillez entrer une adresse e-mail valide');
            return false;
        }
        
        // Si on arrive ici, la validation est réussie
        clearError('email');
        return true;
    }
    
    function validatePhone(phone) {
        // Le téléphone est optionnel, donc si vide, c'est valide
        if (!phone || !phone.trim()) {
            clearError('phone');
            return true;
        }
        
        // Expression régulière pour les numéros de téléphone internationaux
        const phoneRegex = /^[\+\d\s\(\)\-]+$/;
        
        if (!phoneRegex.test(phone.trim())) {
            showError('phone', 'Veuillez entrer un numéro de téléphone valide');
            return false;
        }
        
        // Si on arrive ici, la validation est réussie
        clearError('phone');
        return true;
    }

    // ==================== SOUMISSION DU FORMULAIRE ====================
    
    if (profileForm) {
        profileForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            console.log('Soumission du formulaire démarrée');
            
            try {
                // Nettoyage des erreurs précédentes
                clearAllErrors();
                
                // Validation finale
                const fullNameValid = fullNameInput ? validateFullName(fullNameInput.value) : false;
                const emailValid = emailInput ? validateEmail(emailInput.value) : false;
                const phoneValid = phoneInput ? validatePhone(phoneInput.value) : true;
                
                if (!fullNameValid || !emailValid || !phoneValid) {
                    console.log('Validation échouée');
                    showToast('Veuillez corriger les erreurs dans le formulaire', 'error');
                    return;
                }
                
                // Désactive le bouton et affiche le loader
                saveProfileBtn.disabled = true;
                if (saveText) saveText.classList.add('hidden');
                if (saveLoader) saveLoader.classList.remove('hidden');
                
                // Prépare les données
                const formData = new FormData();
                formData.append('full_name', fullNameInput ? fullNameInput.value.trim() : '');
                formData.append('email', emailInput ? emailInput.value.trim() : '');
                formData.append('phone', phoneInput ? phoneInput.value.trim() : '');
                
                // Ajoute un indicateur pour la suppression de la photo si nécessaire
                if (deletePhoto) {
                    formData.append('delete_picture', 'true');
                    console.log('Suppression de la photo demandée');
                }
                
                // Ajoute la nouvelle photo si sélectionnée
                if (selectedFile) {
                    formData.append('profile_picture', selectedFile);
                    console.log('Fichier sélectionné:', selectedFile.name);
                }
                
                // Récupère le token CSRF
                const csrftoken = getCookie('csrftoken');
                if (!csrftoken) {
                    console.error('CSRF token non trouvé');
                    throw new Error('Erreur de sécurité. Veuillez rafraîchir la page.');
                }
                
                console.log('Envoi de la requête AJAX...');
                
                // Envoie la requête AJAX
                const response = await fetch('/api/profile/update/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    body: formData,
                    credentials: 'same-origin'
                });
                
                console.log('Réponse reçue, statut:', response.status);
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    console.error('Erreur de réponse:', errorData);
                    
                    // Si nous avons des erreurs de validation, on les affiche
                    if (errorData.errors) {
                        return Promise.reject({ 
                            message: 'Erreur de validation', 
                            errors: errorData.errors 
                        });
                    }
                    
                    throw new Error(errorData.message || 'Erreur lors de la mise à jour du profil');
                }
                
                const data = await response.json();
                console.log('Données reçues:', data);
                
                if (data.success) {
                    console.log('Mise à jour réussie, mise à jour de l\'interface...');
                    // Met à jour l'interface
                    if (data.data) {
                        updateUI(data.data);
                    }
                    
                    // Ferme la modale
                    closeModal();
                    
                    // Affiche le toast de succès
                    showToast(data.message || 'Profil mis à jour avec succès', 'success');
                } else {
                    console.log('Erreurs de validation:', data.errors);
                    // Affiche les erreurs
                    if (data.errors) {
                        for (const field in data.errors) {
                            showError(field, data.errors[field]);
                        }
                    } else {
                        showToast(data.message || 'Une erreur est survenue', 'error');
                    }
                }
            } catch (error) {
                console.error('Erreur lors de la mise à jour du profil:', error);
                
                // Affiche les erreurs de validation si elles existent
                if (error.errors) {
                    // Réinitialise d'abord toutes les erreurs
                    clearAllErrors();
                    
                    // Affiche chaque erreur de validation
                    for (const [field, message] of Object.entries(error.errors)) {
                        console.log(`Erreur sur le champ ${field}:`, message);
                        showError(field, message);
                    }
                    
                    // Affiche un message d'erreur général
                    showToast('Veuillez corriger les erreurs dans le formulaire', 'error');
                } else {
                    // Pour les autres types d'erreurs, affiche simplement le message
                    showToast(error.message || 'Erreur lors de la mise à jour du profil', 'error');
                }
            } finally {
                // Réactive le bouton
                if (saveProfileBtn) saveProfileBtn.disabled = false;
                if (saveText) saveText.classList.remove('hidden');
                if (saveLoader) saveLoader.classList.add('hidden');
            }
        });
    }

    // ==================== MISE À JOUR DE L'INTERFACE ====================
    
    function updateUI(data) {
        // Met à jour le nom dans la sidebar
        if (sidebarUserName) {
            sidebarUserName.textContent = data.full_name;
        }
        
        // Met à jour l'image de profil dans la sidebar
        if (data.profile_picture_url) {
            if (sidebarAvatarImg) {
                sidebarAvatarImg.src = data.profile_picture_url;
                safeClassList(sidebarAvatarImg, 'remove', 'hidden');
                if (sidebarAvatarInitials) safeClassList(sidebarAvatarInitials, 'add', 'hidden');
            }
            // Mettre à jour le texte du bouton
            if (uploadPhotoBtn) {
                uploadPhotoBtn.innerHTML = `
                    <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    Changer la photo
                `;
            }
            // Afficher le bouton de suppression
            if (deletePhotoBtn) safeClassList(deletePhotoBtn, 'remove', 'hidden');
        } else {
            if (sidebarAvatarImg) safeClassList(sidebarAvatarImg, 'add', 'hidden');
            if (sidebarAvatarInitials) {
                sidebarAvatarInitials.textContent = data.initials || '';
                safeClassList(sidebarAvatarInitials, 'remove', 'hidden');
            }
            // Mettre à jour le texte du bouton
            if (uploadPhotoBtn) {
                uploadPhotoBtn.innerHTML = `
                    <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    Définir la photo
                `;
            }
            // Masquer le bouton de suppression
            if (deletePhotoBtn) safeClassList(deletePhotoBtn, 'add', 'hidden');
        }
        
        // Met à jour les initiales dans la modale
        if (modalAvatarPreviewInitials) {
            modalAvatarPreviewInitials.textContent = data.initials;
        }
    }

    // ==================== GESTION DES ERREURS ====================
    
    function showError(field, message) {
        const errorElement = document.getElementById('error-' + field);
        const inputElement = document.getElementById('modal-' + field.replace('_', '-'));
        
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.remove('hidden');
        }
        
        if (inputElement) {
            inputElement.classList.add('border-red-500', 'focus:ring-red-500');
            inputElement.classList.remove('border-gray-300', 'focus:ring-blue-500');
        }
    }
    
    function clearError(field) {
        const errorElement = document.getElementById('error-' + field);
        const inputElement = document.getElementById('modal-' + field.replace('_', '-'));
        
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.classList.add('hidden');
        }
        
        if (inputElement) {
            inputElement.classList.remove('border-red-500', 'focus:ring-red-500');
            inputElement.classList.add('border-gray-300', 'focus:ring-blue-500');
        }
    }
    
    function clearAllErrors() {
        clearError('full_name');
        clearError('email');
        clearError('phone');
    }

    // ==================== TOAST DE NOTIFICATION ====================
    
    function showToast(message, type) {
        if (!toastNotification || !toastMessage || !toastIcon) return;
        
        toastMessage.textContent = message;
        
        // Icône selon le type
        if (type === 'success') {
            toastIcon.innerHTML = '<svg class="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>';
        } else {
            toastIcon.innerHTML = '<svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>';
        }
        
        toastNotification.classList.remove('hidden');
        
        // Ferme automatiquement après 5 secondes
        setTimeout(function() {
            toastNotification.classList.add('hidden');
        }, 5000);
    }
    
    if (closeToastBtn) {
        closeToastBtn.addEventListener('click', function() {
            toastNotification.classList.add('hidden');
        });
    }

    // ==================== UTILITAIRES ====================
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

