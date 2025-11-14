// Gestion du tableau de bord superuser - Statistiques en temps réel

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Tableau de bord superuser initialisé');
    
    // Éléments du DOM
    const refreshBtn = document.getElementById('refresh-stats-btn');
    const lastUpdateTime = document.getElementById('last-update-time');
    const statsContainer = document.getElementById('stats-container');
    
    // Éléments de statistiques
    let statElements = {
        total: document.getElementById('stat-total'),
        users: document.getElementById('stat-users'),
        superusers: document.getElementById('stat-superusers'),
        active: document.getElementById('stat-active'),
        inactive: document.getElementById('stat-inactive')
    };
    
    // Récupérer tous les éléments de statistiques de rôle
    function updateRoleStatElements() {
        // Mettre à jour les éléments de base
        statElements = {
            total: document.getElementById('stat-total'),
            users: document.getElementById('stat-users'),
            superusers: document.getElementById('stat-superusers'),
            active: document.getElementById('stat-active'),
            inactive: document.getElementById('stat-inactive')
        };
        
        // Ajouter les éléments de rôle dynamiques
        document.querySelectorAll('[id^="stat-role-"]').forEach(el => {
            const roleId = el.id.replace('stat-role-', '');
            statElements[`role_${roleId}`] = el;
        });
    }
    
    // Initialiser les éléments de rôle
    updateRoleStatElements();
    
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
            console.log('🔄 Tentative de récupération des statistiques...');
            
            // Récupérer les données mises à jour via AJAX
            const response = await fetch('/api/superuser-dashboard/stats/', {
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });
            
            console.log('📊 Réponse reçue:', response);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ Erreur HTTP:', response.status, errorText);
                throw new Error(`Erreur HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('📦 Données reçues:', data);
            
            if (data.status === 'error') {
                console.error('❌ Erreur côté serveur:', data.message);
                throw new Error(data.message || 'Erreur inconnue du serveur');
            }
            
            // Mettre à jour l'heure de dernière mise à jour
            if (lastUpdateTime) {
                const now = new Date();
                lastUpdateTime.textContent = now.toLocaleTimeString();
            }
            
            // Mettre à jour les statistiques existantes
            if (data.stats) {
                console.log('🔄 Mise à jour des statistiques principales');
                for (const [key, value] of Object.entries(data.stats)) {
                    const element = document.getElementById(`stat-${key}`);
                    if (element) {
                        const currentValue = parseInt(element.textContent) || 0;
                        console.log(`📊 Mise à jour ${key}: ${currentValue} → ${value}`);
                        animateValue(element, currentValue, value, 500);
                    } else {
                        console.warn(`⚠️ Élément non trouvé: stat-${key}`);
                    }
                }
            } else {
                console.warn('⚠️ Aucune statistique principale trouvée dans la réponse');
            }
            
            // Mettre à jour les statistiques de rôle
            if (data.role_stats) {
                console.log('🔄 Mise à jour des statistiques de rôle');
                data.role_stats.forEach(role => {
                    console.log(`🔄 Traitement du rôle: ${role.name} (ID: ${role.id})`);
                    
                    // Vérifier si la carte de rôle existe déjà
                    const roleCard = document.getElementById(`role-card-${role.id}`);
                    const roleCountElement = document.getElementById(`stat-role-${role.id}`);
                    
                    if (roleCountElement) {
                        // Mettre à jour le compteur existant
                        const currentValue = parseInt(roleCountElement.textContent) || 0;
                        console.log(`🔄 Mise à jour du compteur pour le rôle ${role.name}: ${currentValue} → ${role.count}`);
                        animateValue(roleCountElement, currentValue, role.count, 500);
                    } else if (!role.is_system) {
                        // Créer une nouvelle carte pour le rôle
                        console.log(`➕ Création d'une nouvelle carte pour le rôle: ${role.name}`);
                        createRoleCard(role);
                    }
                });
                
                // Mettre à jour les références aux éléments de statistiques
                updateRoleStatElements();
            } else {
                console.warn('⚠️ Aucune statistique de rôle trouvée dans la réponse');
            }
            
            console.log('✅ Mise à jour des statistiques terminée avec succès');
            showNotification('Statistiques mises à jour avec succès', 'success');
            
        } catch (error) {
            console.error('❌ Erreur lors de l\'actualisation:', error);
            showNotification(`Erreur: ${error.message || 'Impossible de récupérer les statistiques'}`, 'error');
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
    function animateAllStats() {
        Object.entries(statElements).forEach(([key, element]) => {
            if (element) {
                const finalValue = parseInt(element.textContent) || 0;
                element.textContent = '0';
                setTimeout(() => {
                    animateValue(element, 0, finalValue, 1000);
                }, 100);
            }
        });
    }
    
    // Animer les statistiques au chargement
    animateAllStats();
    
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
    
    // ==================== FONCTIONS UTILITAIRES ====================
    
    // Créer une nouvelle carte de rôle
    function createRoleCard(role) {
        // Créer l'élément de la carte
        const card = document.createElement('div');
        card.className = 'stat-card gradient-border bg-white rounded-xl p-6 shadow-xl scale-in';
        card.id = `role-card-${role.id}`;
        
        // Définir un délai d'animation basé sur l'ID du rôle pour un effet en cascade
        const animationDelay = 0.5 + (role.id % 5) * 0.1;
        card.style.animationDelay = `${animationDelay}s`;
        
        // Définir le contenu HTML de la carte
        card.innerHTML = `
            <div class="flex items-center justify-between mb-4">
                <div class="p-4 bg-gradient-to-br from-indigo-100 to-indigo-200 rounded-xl">
                    <svg class="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                    </svg>
                </div>
            </div>
            <h3 class="text-gray-500 text-sm font-semibold mb-2 uppercase tracking-wider">${role.display_name || role.name.charAt(0).toUpperCase() + role.name.slice(1)}</h3>
            <p class="stat-number" id="stat-role-${role.id}">${role.count || 0}</p>
            <div class="mt-3 flex items-center text-xs text-gray-500">
                <span class="px-2 py-1 bg-indigo-100 text-indigo-800 rounded-full font-semibold">Rôle: ${role.name}</span>
            </div>
        `;
        
        // Ajouter les gestionnaires d'événements pour les effets de survol
        addHoverEffects(card);
        
        // Ajouter la carte au conteneur
        if (statsContainer) {
            statsContainer.appendChild(card);
            
            // Animer le compteur
            const counter = card.querySelector(`#stat-role-${role.id}`);
            if (counter) {
                const finalValue = parseInt(counter.textContent) || 0;
                counter.textContent = '0';
                setTimeout(() => {
                    animateValue(counter, 0, finalValue, 1000);
                }, animationDelay * 1000);
            }
        }
        
        return card;
    }
    
    // Ajouter des effets de survol à une carte
    function addHoverEffects(card) {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
            this.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '';
        });
    }
    
    // ==================== EFFETS VISUELS SUPPLÉMENTAIRES ====================
    
    // Appliquer les effets de survol à toutes les cartes existantes
    document.querySelectorAll('.stat-card').forEach(card => {
        addHoverEffects(card);
    });
    
    // Actualisation automatique toutes les 30 secondes
    setInterval(() => {
        if (!document.hidden) {  // Ne pas actualiser si l'onglet n'est pas actif
            console.log('🔄 Actualisation automatique des statistiques...');
            refreshStats();
        }
    }, 30000);
    
    console.log('✅ Tableau de bord superuser prêt');
});