/**
 * Fichier de gestion des alertes personnalisées avec SweetAlert2
 * Ce fichier étend les fonctionnalités de base de SweetAlert2
 * avec des styles et des comportements personnalisés.
 */

// Configuration globale de SweetAlert2
const Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 5000,
    timerProgressBar: true,
    didOpen: (toast) => {
        toast.addEventListener('mouseenter', Swal.stopTimer);
        toast.addEventListener('mouseleave', Swal.resumeTimer);
    }
});

// Alerte de succès
function showSuccess(message, title = 'Succès !') {
    return Swal.fire({
        title: title,
        text: message,
        icon: 'success',
        confirmButtonText: 'OK',
        confirmButtonColor: '#3085d6',
        customClass: {
            popup: 'animated fadeInDown faster',
            confirmButton: 'btn btn-success'
        }
    });
}

// Alerte d'erreur
function showError(message, title = 'Erreur !') {
    return Swal.fire({
        title: title,
        html: message,
        icon: 'error',
        confirmButtonText: 'OK',
        confirmButtonColor: '#d33',
        customClass: {
            popup: 'animated shake',
            confirmButton: 'btn btn-danger'
        }
    });
}

// Alerte d'avertissement
function showWarning(message, title = 'Attention !') {
    return Swal.fire({
        title: title,
        text: message,
        icon: 'warning',
        confirmButtonText: 'Compris',
        confirmButtonColor: '#ffc107',
        customClass: {
            popup: 'animated pulse',
            confirmButton: 'btn btn-warning text-white'
        }
    });
}

// Boîte de dialogue de confirmation
function confirmAction(options) {
    const defaultOptions = {
        title: 'Êtes-vous sûr ?',
        text: 'Cette action est irréversible',
        confirmButtonText: 'Oui, continuer',
        cancelButtonText: 'Annuler',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        reverseButtons: true,
        focusCancel: true,
        customClass: {
            popup: 'animated fadeInDown faster',
            confirmButton: 'btn btn-primary',
            cancelButton: 'btn btn-outline-secondary'
        }
    };
    
    return Swal.fire({
        ...defaultOptions,
        ...options
    });
}

// Alerte avec entrée de texte
function promptInput(options) {
    const defaultOptions = {
        title: 'Entrez une valeur',
        input: 'text',
        showCancelButton: true,
        confirmButtonText: 'Valider',
        cancelButtonText: 'Annuler',
        inputValidator: (value) => {
            if (!value) {
                return 'Ce champ est requis !';
            }
        }
    };
    
    return Swal.fire({
        ...defaultOptions,
        ...options
    });
}

// Alerte de chargement
function showLoading(title = 'Traitement en cours...') {
    return Swal.fire({
        title: title,
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
}

// Alerte de succès avec redirection
function showSuccessWithRedirect(message, redirectUrl, title = 'Succès !') {
    return Swal.fire({
        title: title,
        text: message,
        icon: 'success',
        showConfirmButton: true,
        confirmButtonText: 'OK',
        allowOutsideClick: false
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = redirectUrl;
        }
    });
}

// Exporter les fonctions pour une utilisation globale
window.showSuccess = showSuccess;
window.showError = showError;
window.showWarning = showWarning;
window.confirmAction = confirmAction;
window.promptInput = promptInput;
window.showLoading = showLoading;
window.showSuccessWithRedirect = showSuccessWithRedirect;

// Surcharger la fonction alert() native
window.originalAlert = window.alert;
window.alert = function(message) {
    return showSuccess(message, 'Information');
};

// Gestion des messages flash Django
$(document).ready(function() {
    // Vérifier s'il y a des messages à afficher
    const messages = $('.messages');
    if (messages.length > 0) {
        messages.each(function() {
            const type = $(this).data('type') || 'info';
            const message = $(this).text().trim();
            
            switch(type) {
                case 'success':
                    showSuccess(message);
                    break;
                case 'error':
                    showError(message);
                    break;
                case 'warning':
                    showWarning(message);
                    break;
                default:
                    Toast.fire({
                        icon: type,
                        title: message
                    });
            }
            
            // Supprimer le message après l'avoir affiché
            $(this).remove();
        });
    }
});
