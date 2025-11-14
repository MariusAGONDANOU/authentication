// Gestion du tableau de bord superuser - Statistiques en temps réel

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Tableau de bord superuser initialisé');
    
    // Éléments du DOM
    const refreshBtn = document.getElementById('refresh-stats-btn');
    const lastUpdateTime = document.getElementById('last-update-time');
    
    // Éléments de statistiques
    const statElements = {
        total: document.getElementById('stat-total'),
        users: document.getElementById('stat-users'),
        superusers: document.getElementById('stat-superusers'),
        active: document.getElementById('stat-active'),
        inactive: document.getElementById('stat-inactive')
    };
    
    // État de chargement
    let isLoading = false;
    
    // ==================== ACTUALISATION DES STATISTIQUES ====================
    
    async function refreshStats() {
        if (isLoading) return;
        
        isLoading = true;
        
        // Animation de rotation du bouton
        if (refreshBtn) {
            refreshBtn.classList.add('animate-spin');
            refreshBtn.disabled = true;
        }
        
        try {
            // Simulation d'actualisation (à remplacer par un vrai appel API si nécessaire)
            // Pour l'instant, on recharge simplement la page
            window.location.reload();
            
        } catch (error) {
            console.error('❌ Erreur lors de l\'actualisation:', error);
            showNotification('Erreur lors de l\'actualisation des statistiques', 'error');
        } finally {
            isLoading = false;
            
            // Arrêt de l'animation
            if (refreshBtn) {
                setTimeout(() => {
                    refreshBtn.classList.remove('animate-spin');
                    refreshBtn.disabled = false;
                }, 500);
            }
        }
    }
    
    // ==================== ANIMATION DES CHIFFRES ====================
    
    function animateValue(element, start, end, duration) {
        if (!element) return;
        
        const range = end - start;
        const increment = range / (duration / 16); // 60 FPS
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
                
                // Effet de pulsation
                element.parentElement.classList.add('scale-110');
                setTimeout(() => {
                    element.parentElement.classList.remove('scale-110');
                }, 200);
            }
            element.textContent = Math.round(current);
        }, 16);
    }
    
    // Animation au chargement
    Object.values(statElements).forEach(element => {
        if (element) {
            const finalValue = parseInt(element.textContent);
            element.textContent = '0';
            setTimeout(() => {
                animateValue(element, 0, finalValue, 1000);
            }, 100);
        }
    });
    
    // ==================== NOTIFICATION TOAST ====================
    
    function showNotification(message, type = 'success') {
        // Création du toast
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-lg shadow-xl transform transition-all duration-300 ${
            type === 'success' ? 'bg-green-500' : 'bg-red-500'
        } text-white flex items-center gap-3`;
        
        toast.innerHTML = `
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                ${type === 'success' 
                    ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>'
                    : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>'
                }
            </svg>
            <span class="font-medium">${message}</span>
        `;
        
        document.body.appendChild(toast);
        
        // Animation d'entrée
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 10);
        
        // Suppression automatique après 3 secondes
        setTimeout(() => {
            toast.style.transform = 'translateX(400px)';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
    
    // ==================== EVENT LISTENERS ====================
    
    // Bouton d'actualisation
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshStats);
    }
    
    // Actualisation automatique toutes les 30 secondes (optionnel)
    // Décommentez si vous souhaitez une actualisation automatique
    /*
    setInterval(() => {
        console.log('🔄 Actualisation automatique des statistiques...');
        refreshStats();
    }, 30000);
    */
    
    // ==================== EFFETS VISUELS SUPPLÉMENTAIRES ====================
    
    // Effet de survol sur les cartes de statistiques
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    console.log('✅ Tableau de bord superuser prêt');
});