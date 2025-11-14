// Gestion des rôles - Actions AJAX

// Toast de notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast-notification');
    const toastMessage = document.getElementById('toast-message');
    const toastIcon = document.getElementById('toast-icon');
    
    if (!toast || !toastMessage || !toastIcon) return;
    
    toastMessage.textContent = message;
    
    // Icône selon le type
    if (type === 'success') {
        toastIcon.innerHTML = '<svg class="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>';
    } else {
        toastIcon.innerHTML = '<svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>';
    }
    
    toast.classList.remove('hidden');
    
    // Ferme automatiquement après 5 secondes
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 5000);
}

// Fermer le toast
document.addEventListener('DOMContentLoaded', function() {
    const closeToastBtn = document.getElementById('close-toast-btn');
    if (closeToastBtn) {
        closeToastBtn.addEventListener('click', () => {
            document.getElementById('toast-notification').classList.add('hidden');
        });
    }
});

// Récupérer le token CSRF
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

// Confirmer suppression de rôle
function confirmDeleteRole(roleId, roleName, userCount) {
    if (userCount > 0) {
        showToast(`Impossible de supprimer ce rôle. ${userCount} utilisateur(s) l'utilisent encore.`, 'error');
        return;
    }
    
    if (confirm(`Êtes-vous sûr de vouloir supprimer le rôle "${roleName}" ?\n\nCette action est irréversible.`)) {
        deleteRole(roleId, roleName);
    }
}

// Supprimer un rôle
function deleteRole(roleId, roleName) {
    const csrftoken = getCookie('csrftoken');
    
    fetch(`/gestion-roles/${roleId}/supprimer/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Supprime la card du DOM
            const card = document.querySelector(`[data-role-id="${roleId}"]`);
            if (card) {
                card.style.opacity = '0';
                card.style.transform = 'scale(0.9)';
                setTimeout(() => {
                    card.remove();
                    
                    // Si plus aucun rôle personnalisé, afficher le message vide
                    const customRolesGrid = card.parentElement;
                    if (customRolesGrid && customRolesGrid.children.length === 0) {
                        window.location.reload();
                    }
                }, 300);
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

// Animation CSS pour le toast
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    .animate-slide-in { animation: slideIn 0.3s ease-out; }
`;
document.head.appendChild(style);