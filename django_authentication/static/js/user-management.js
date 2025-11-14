// Gestion des utilisateurs - Actions AJAX

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

// Toggle statut utilisateur
function toggleUserStatus(userId, currentStatus) {
    if (!confirm('Êtes-vous sûr de vouloir modifier le statut de cet utilisateur ?')) {
        return;
    }
    
    const csrftoken = getCookie('csrftoken');
    
    fetch(`/admin/users/${userId}/toggle-status/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Met à jour le bouton
            const statusButton = document.querySelector(`.status-toggle[data-user-id="${userId}"]`);
            const statusText = document.querySelector(`.status-text-${userId}`);
            
            if (statusButton && statusText) {
                if (data.is_active) {
                    statusButton.className = 'status-toggle px-3 py-1 text-xs font-semibold rounded-full transition-all bg-green-100 text-green-800 hover:bg-green-200';
                    statusText.textContent = 'Actif';
                } else {
                    statusButton.className = 'status-toggle px-3 py-1 text-xs font-semibold rounded-full transition-all bg-red-100 text-red-800 hover:bg-red-200';
                    statusText.textContent = 'Inactif';
                }
            }
            
            showToast(data.message, 'success');
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showToast('Erreur lors de la modification du statut', 'error');
    });
}

// Confirmer suppression
function confirmDelete(userId, userName) {
    if (confirm(`Êtes-vous sûr de vouloir supprimer l'utilisateur "${userName}" ?\n\nCette action est irréversible.`)) {
        deleteUser(userId, userName);
    }
}

// Supprimer utilisateur
function deleteUser(userId, userName) {
    const csrftoken = getCookie('csrftoken');
    
    fetch(`/admin/users/${userId}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Supprime la ligne du tableau
            const row = document.querySelector(`tr[data-user-id="${userId}"]`);
            if (row) {
                row.style.opacity = '0';
                row.style.transform = 'translateX(-20px)';
                setTimeout(() => {
                    row.remove();
                }, 300);
            }
            
            showToast(data.message, 'success');
            
            // Recharge la page après 2 secondes si plus aucun utilisateur
            setTimeout(() => {
                const tbody = document.querySelector('tbody');
                if (tbody && tbody.querySelectorAll('tr').length === 0) {
                    window.location.reload();
                }
            }, 2000);
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showToast('Erreur lors de la suppression', 'error');
    });
}