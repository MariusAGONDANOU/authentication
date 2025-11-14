from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from .forms import SignupForm, RoleManagementForm
from .models import User, Role
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse, Http404
from .forms import LoginForm
import time
from django.views.decorators.http import require_POST, require_GET
from django.core.files.base import ContentFile
import json
import base64
from .forms import ProfileUpdateForm
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .forms import UserManagementForm
from functools import wraps
from django.urls import reverse
from .forms import UserManagementForm
from django.views.decorators.cache import never_cache

def superuser_required(view_func):
    """Décorateur pour vérifier que l'utilisateur est superuser"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user_obj
        
        # Vérification cohérente du rôle superuser
        if not user.role or user.role.name != 'superuser':
            messages.error(request, 'Accès non autorisé. Droits administrateur requis.')
            return redirect('user_dashboard')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def home_view(request):
    """Page d'accueil avec liens vers inscription/connexion"""
    return render(request, 'home.html')
    
@csrf_protect
@require_http_methods(["GET", "POST"])
def signup_view(request):
    """Vue d'inscription avec gestion complète du formulaire"""
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        
        if form.is_valid():
            try:
                # Création de l'utilisateur
                user = form.save(commit=False)
                user.phone = form.cleaned_data['phone_number']
                user.set_password(form.cleaned_data['password'])
                user.save()
                
                messages.success(
                    request,
                    'Inscription réussie ! Vous pouvez maintenant vous connecter.'
                )
                return redirect('login')
                
            except Exception as e:
                messages.error(
                    request,
                    'Une erreur est survenue lors de l\'inscription. Veuillez réessayer.'
                )
                print(f"Erreur d'inscription: {str(e)}")
        else:
            messages.error(
                request,
                'Veuillez corriger les erreurs dans le formulaire.'
            )
    else:
        form = SignupForm()
    
    # Liste des pays avec indicatifs (sélection des plus courants)
    countries = [
        {'code': '+229', 'name': 'Bénin', 'flag': '🇧🇯', 'iso': 'BJ'},
        {'code': '+33', 'name': 'France', 'flag': '🇫🇷', 'iso': 'FR'},
        {'code': '+1', 'name': 'États-Unis/Canada', 'flag': '🇺🇸', 'iso': 'US'},
        {'code': '+44', 'name': 'Royaume-Uni', 'flag': '🇬🇧', 'iso': 'GB'},
        {'code': '+225', 'name': 'Côte d\'Ivoire', 'flag': '🇨🇮', 'iso': 'CI'},
        {'code': '+221', 'name': 'Sénégal', 'flag': '🇸🇳', 'iso': 'SN'},
        {'code': '+228', 'name': 'Togo', 'flag': '🇹🇬', 'iso': 'TG'},
        {'code': '+226', 'name': 'Burkina Faso', 'flag': '🇧🇫', 'iso': 'BF'},
        {'code': '+227', 'name': 'Niger', 'flag': '🇳🇪', 'iso': 'NE'},
        {'code': '+237', 'name': 'Cameroun', 'flag': '🇨🇲', 'iso': 'CM'},
        {'code': '+212', 'name': 'Maroc', 'flag': '🇲🇦', 'iso': 'MA'},
        {'code': '+213', 'name': 'Algérie', 'flag': '🇩🇿', 'iso': 'DZ'},
        {'code': '+216', 'name': 'Tunisie', 'flag': '🇹🇳', 'iso': 'TN'},
        {'code': '+234', 'name': 'Nigeria', 'flag': '🇳🇬', 'iso': 'NG'},
        {'code': '+233', 'name': 'Ghana', 'flag': '🇬🇭', 'iso': 'GH'},
        {'code': '+32', 'name': 'Belgique', 'flag': '🇧🇪', 'iso': 'BE'},
        {'code': '+41', 'name': 'Suisse', 'flag': '🇨🇭', 'iso': 'CH'},
        {'code': '+49', 'name': 'Allemagne', 'flag': '🇩🇪', 'iso': 'DE'},
        {'code': '+39', 'name': 'Italie', 'flag': '🇮🇹', 'iso': 'IT'},
        {'code': '+34', 'name': 'Espagne', 'flag': '🇪🇸', 'iso': 'ES'},
    ]
    
    context = {
        'form': form,
        'countries': countries,
    }
    
    return render(request, 'registration/signup.html', context)


# Configuration du throttling
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # 5 minutes en secondes


def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vue de connexion avec protection contre force brute"""
    
    client_ip = get_client_ip(request)
    cache_key = f'login_attempts_{client_ip}'
    attempts = cache.get(cache_key, 0)
    
    if attempts >= MAX_LOGIN_ATTEMPTS:
        lockout_key = f'login_lockout_{client_ip}'
        lockout_time = cache.get(lockout_key)
        
        if lockout_time:
            remaining_time = int((lockout_time - time.time()) / 60)
            messages.error(
                request,
                f'Trop de tentatives de connexion. Veuillez réessayer dans {remaining_time} minutes.'
            )
            return render(request, 'registration/login.html', {'form': LoginForm(), 'locked_out': True})
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            user = form.get_user()
            
            if user is not None:
                # Connexion réussie
                cache.delete(cache_key)
                cache.delete(f'login_lockout_{client_ip}')
                
                # Création de la session
                request.session['user_id'] = user.id
                request.session['user_email'] = user.email
                # Stocker le nom du rôle au lieu de l'objet
                request.session['user_role'] = user.role.name if user.role else 'user'
                
                # Gestion "Se souvenir de moi"
                if form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(1209600)  # 14 jours
                else:
                    request.session.set_expiry(0)
                
                messages.success(request, f'Bienvenue, {user.full_name} !')
                
                # DEBUG: Afficher les informations de l'utilisateur
                print("\n" + "="*50)
                print("=== DEBUG CONNEXION ===")
                print(f"Utilisateur: {user.email}")
                print(f"is_superuser: {getattr(user, 'is_superuser', 'Non défini')}")
                print(f"is_staff: {getattr(user, 'is_staff', 'Non défini')}")
                print(f"role: {getattr(user, 'role', 'Aucun rôle')}")
                if hasattr(user, 'role') and user.role:
                    print(f"role.name: {user.role.name}")
                
                # Vérification des conditions de redirection
                is_super = getattr(user, 'is_superuser', False)
                has_role = hasattr(user, 'role') and user.role and user.role.name == 'superuser'
                
                print(f"\n=== VERIFICATION REDIRECTION ===")
                print(f"is_superuser: {is_super}")
                print(f"has superuser role: {has_role}")
                
                # REDIRECTION SELON LE RÔLE
                if is_super or has_role:
                    print("\n=== REDIRECTION ===")
                    print("Cible: superuser_dashboard")
                    print(f"URL: {reverse('superuser_dashboard')}")
                    return redirect('superuser_dashboard')
                elif hasattr(user, 'role') and user.role:
                    # Vérifier si c'est un rôle personnalisé (ni user ni superuser)
                    if user.role.name not in ['user', 'superuser']:
                        print("\n=== REDIRECTION ===")
                        print(f"Cible: role_dashboard pour le rôle {user.role.name}")
                        print(f"URL: {reverse('role_dashboard', args=[user.role.id])}")
                        return redirect('role_dashboard', role_id=user.role.id)
                
                # Par défaut, rediriger vers le tableau de bord utilisateur standard
                print("\n=== REDIRECTION ===")
                print("Cible: user_dashboard (par défaut)")
                print(f"URL: {reverse('user_dashboard')}")
                return redirect('user_dashboard')
        else:
            # Tentative échouée
            attempts += 1
            cache.set(cache_key, attempts, LOCKOUT_DURATION)
            
            if attempts >= MAX_LOGIN_ATTEMPTS:
                lockout_time = time.time() + LOCKOUT_DURATION
                cache.set(f'login_lockout_{client_ip}', lockout_time, LOCKOUT_DURATION)
                messages.error(request, 'Trop de tentatives de connexion.')
            else:
                remaining_attempts = MAX_LOGIN_ATTEMPTS - attempts
                messages.error(request, f'Identifiants incorrects. {remaining_attempts} tentatives restantes.')
    else:
        form = LoginForm()
    
    return render(request, 'registration/login.html', {'form': form})

def login_required_custom(view_func):
    """Décorateur personnalisé pour vérifier l'authentification"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Vérifie si l'utilisateur est authentifié via la session
        if 'user_id' not in request.session:
            messages.error(request, 'Veuillez vous connecter pour accéder à cette page.')
            return redirect('login')
            
        # Récupère l'utilisateur depuis la base de données
        try:
            user = User.objects.select_related('role').get(id=request.session['user_id'])
            request.user_obj = user  # Stocke l'utilisateur dans la requête
            
            # Vérifie si l'utilisateur est actif
            if not user.is_active:
                messages.error(request, 'Votre compte est désactivé. Veuillez contacter un administrateur.')
                return redirect('login')
                
            # Vérifie si l'utilisateur a un rôle valide
            if not user.role:
                messages.error(request, 'Votre compte n\'a pas de rôle défini. Veuillez contacter un administrateur.')
                return redirect('login')
                
            return view_func(request, *args, **kwargs)
            
        except User.DoesNotExist:
            messages.error(request, 'Session expirée. Veuillez vous reconnecter.')
            return redirect('login')
    
    return _wrapped_view

@login_required_custom
def superuser_dashboard_view(request):
    """Tableau de bord administrateur avec statistiques"""
    user = request.user_obj
    
    # Vérification du rôle
    if not user.role or user.role.name != 'superuser':
        messages.error(request, 'Accès non autorisé. Droits administrateur requis.')
        return redirect('user_dashboard' if user.role and user.role.name == 'user' else 'login')
    
    try:
        # Récupération des rôles
        from .models import Role
        
        superuser_role = Role.objects.get(name='superuser')
        user_role = Role.objects.get(name='user')
        
        # Statistiques
        total_users = User.objects.count()
        total_regular_users = User.objects.filter(role=user_role).count()
        total_superusers = User.objects.filter(role=superuser_role).count()
        active_users = User.objects.filter(is_active=True).count()
        inactive_users = User.objects.filter(is_active=False).count()
        
        # Utilisateurs récents avec leurs rôles
        recent_users = User.objects.select_related('role').order_by('-created_at')[:5]
        
        context = {
            'user': user,
            'page_title': 'Tableau de bord administrateur',
            'stats': {
                'total_users': total_users,
                'regular_users': total_regular_users,
                'superusers': total_superusers,
                'active_users': active_users,
                'inactive_users': inactive_users,
            },
            'recent_users': recent_users,
        }
    except Role.DoesNotExist:
        messages.error(request, 'Erreur de configuration: les rôles par défaut n\'existent pas.')
        return redirect('user_dashboard')
    
    return render(request, 'dashboards/superuser_dashboard.html', context)

@login_required_custom
def user_dashboard_view(request):
    """Tableau de bord utilisateur standard"""
    user = request.user_obj
    
    # Vérification du rôle
    if not user.role or user.role.name != 'user':
        messages.error(request, 'Accès non autorisé. Vous devez être un utilisateur standard.')
        return redirect('login')
    
    # Chargement des données spécifiques à l'utilisateur
    context = {
        'user': user,
        'page_title': 'Tableau de bord utilisateur',
        'role_name': 'utilisateur standard'
    }
    
    return render(request, 'dashboards/role_dashboard.html', context)

@login_required_custom
def role_dashboard_view(request, role_id):
    """Tableau de bord pour un rôle personnalisé"""
    user = request.user_obj
    
    # Vérifier que l'utilisateur a bien le rôle demandé
    if not user.role or user.role.id != role_id:
        messages.error(request, 'Accès non autorisé.')
        return redirect('login')
    
    # Récupérer le rôle
    role = get_object_or_404(Role, id=role_id)
    
    # Chargement des données spécifiques au rôle
    context = {
        'user': user,
        'page_title': f'Tableau de bord {role.display_name or role.name}',
        'role_name': role.display_name or role.name
    }
    
    return render(request, 'dashboards/role_dashboard.html', context)

# Décorateur personnalisé pour vérifier l'authentification
def login_required_custom(view_func):
    """Décorateur personnalisé pour vérifier l'authentification"""
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Vous devez être connecté pour accéder à cette page.')
            return redirect('login')
        
        try:
            user = User.objects.get(id=user_id)
            request.user_obj = user
            return view_func(request, *args, **kwargs)
        except User.DoesNotExist:
            request.session.flush()
            messages.error(request, 'Session invalide. Veuillez vous reconnecter.')
            return redirect('login')
    
    return wrapper

@login_required_custom
def user_interface_view(request):
    """Interface utilisateur standard"""
    user = request.user_obj
    
    # Vérification du rôle
    if not user.role:
        messages.error(request, 'Votre compte n\'a pas de rôle défini. Veuillez contacter un administrateur.')
        return redirect('login')
        
    # Si l'utilisateur est un superutilisateur, on le redirige vers l'interface administrateur
    if user.role.name == 'superuser':
        return redirect('superuser_interface')
    
    return render(request, 'interfaces/user_interface.html', {'user': user})

@login_required_custom
def superuser_interface_view(request):
    """Interface super utilisateur"""
    user = request.user_obj
    
    # Vérification du rôle
    if not user.role or user.role.name != 'superuser':
        messages.error(request, 'Accès non autorisé. Droits administrateur requis.')
        return redirect('user_interface' if user.role and user.role.name == 'user' else 'login')
    
    return render(request, 'interfaces/superuser_interface.html', {'user': user})

@login_required_custom
def user_management_list(request):
    """Liste des utilisateurs avec recherche et pagination - VERSION UNIFIÉE"""
    user = request.user_obj
    
    search_query = request.GET.get('search', '').strip()
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    users = User.objects.select_related('role').all().order_by('-created_at')
    
    if search_query:
        users = users.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    if role_filter:
        users = users.filter(role__name=role_filter)
    
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Rôles disponibles pour le filtre
    from .models import Role
    available_roles = Role.objects.all()
    
    context = {
        'user': user,
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'available_roles': available_roles,
        'page_title': 'Gestion des utilisateurs'
    }
    
    return render(request, 'admin/user_management.html', context)

@login_required_custom
def user_create_view(request):
    """Création d'un nouvel utilisateur"""
    admin_user = request.user_obj
    
    if request.method == 'POST':
        form = UserManagementForm(request.POST, request.FILES, is_edit=False)
        
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'Utilisateur {user.full_name} créé avec succès.')
                return redirect('user_management')
            except Exception as e:
                messages.error(request, f'Erreur lors de la création: {str(e)}')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = UserManagementForm(is_edit=False)
    
    context = {
        'user': admin_user,
        'form': form,
        'is_edit': False,
        'page_title': 'Créer un utilisateur',
    }
    
    return render(request, 'admin/user_form.html', context)


@login_required_custom
def user_edit_view(request, user_id):
    """Édition d'un utilisateur existant"""
    admin_user = request.user_obj
    
    try:
        user_to_edit = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Utilisateur introuvable.')
        return redirect('user_management')
    
    if request.method == 'POST':
        form = UserManagementForm(
            request.POST,
            request.FILES,
            instance=user_to_edit,
            is_edit=True
        )
        
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'Utilisateur {user.full_name} modifié avec succès.')
                return redirect('user_management')
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification: {str(e)}')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = UserManagementForm(instance=user_to_edit, is_edit=True)
    
    context = {
        'user': admin_user,
        'form': form,
        'user_to_edit': user_to_edit,
        'is_edit': True,
        'page_title': f'Modifier {user_to_edit.full_name}',
    }
    
    return render(request, 'admin/user_form.html', context)


@csrf_protect
@require_POST
@login_required_custom
def user_delete_view(request, user_id):
    """Suppression d'un utilisateur"""
    admin_user = request.user_obj
    
    try:
        user_to_delete = User.objects.get(id=user_id)
        
        # Empêcher la suppression de soi-même
        if user_to_delete.id == admin_user.id:
            return JsonResponse({
                'success': False,
                'message': 'Vous ne pouvez pas supprimer votre propre compte.'
            }, status=400)
        
        # Empêcher la suppression du dernier superuser
        if user_to_delete.role and user_to_delete.role.name == 'superuser':
            superuser_count = User.objects.filter(role__name='superuser').count()
            if superuser_count <= 1:
                return JsonResponse({
                    'success': False,
                    'message': 'Impossible de supprimer le dernier superutilisateur.'
                }, status=400)
        
        full_name = user_to_delete.full_name
        user_to_delete.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Utilisateur {full_name} supprimé avec succès.'
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Utilisateur introuvable.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=500)


@csrf_protect
@require_POST
@login_required_custom
def user_toggle_status_view(request, user_id):
    """Active/désactive un utilisateur"""
    admin_user = request.user_obj
    
    try:
        user_to_toggle = User.objects.get(id=user_id)
        
        # Empêcher la désactivation de soi-même
        if user_to_toggle.id == admin_user.id:
            return JsonResponse({
                'success': False,
                'message': 'Vous ne pouvez pas modifier votre propre statut.'
            }, status=400)
        
        user_to_toggle.is_active = not user_to_toggle.is_active
        user_to_toggle.save()
        
        status_text = 'activé' if user_to_toggle.is_active else 'désactivé'
        
        return JsonResponse({
            'success': True,
            'message': f'Utilisateur {user_to_toggle.full_name} {status_text}.',
            'is_active': user_to_toggle.is_active
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Utilisateur introuvable.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=500)

@csrf_protect
@require_http_methods(["POST"])
def logout_view(request):
    """Vue de déconnexion"""
    # Stocker le message de déconnexion
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    
    # Nettoyer les données de session
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'user_email' in request.session:
        del request.session['user_email']
    if 'user_role' in request.session:
        del request.session['user_role']
    
    # Vider complètement la session
    request.session.flush()
    
    # Rediriger vers la page de connexion ou la page demandée
    next_page = request.POST.get('next', 'login')
    return redirect(next_page)


def reset_password_view(request):
    """Page de réinitialisation de mot de passe (placeholder)"""
    return render(request, 'registration/reset_password.html')


def login_required_custom(view_func):
    """Décorateur personnalisé pour vérifier l'authentification"""
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'Vous devez être connecté pour accéder à cette page.')
            return redirect('login')
        
        try:
            user = User.objects.get(id=user_id)
            request.user_obj = user
            return view_func(request, *args, **kwargs)
        except User.DoesNotExist:
            request.session.flush()
            messages.error(request, 'Session invalide. Veuillez vous reconnecter.')
            return redirect('login')
    
    return wrapper

@login_required_custom
def user_dashboard_view(request):
    """Tableau de bord utilisateur standard"""
    user = request.user_obj
    
    # Vérification du rôle
    if not user.role:
        messages.error(request, 'Votre compte n\'a pas de rôle défini. Veuillez contacter un administrateur.')
        return redirect('login')
        
    # Si l'utilisateur est un superutilisateur, on le redirige vers le tableau de bord administrateur
    if user.role.name == 'superuser':
        return redirect('superuser_dashboard')
    
    # Chargement des données spécifiques à l'utilisateur
    context = {
        'user': user,
        'page_title': 'Tableau de bord utilisateur'
    }
    
    return render(request, 'dashboards/user_dashboard.html', context)

def get_dashboard_stats():
    """Fonction utilitaire pour récupérer les statistiques du tableau de bord"""
    from .models import Role, User
    
    # Récupération de tous les rôles
    roles = Role.objects.all()
    
    # Statistiques de base
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'inactive_users': User.objects.filter(is_active=False).count(),
    }
    
    # Ajout du comptage par rôle
    role_stats = []
    for role in roles:
        role_stats.append({
            'id': role.id,
            'name': role.name,
            'display_name': role.display_name or role.name.capitalize(),
            'count': User.objects.filter(role=role).count(),
            'is_system': role.name in ['user', 'superuser']
        })
        
        # Ajout au stats générales pour la rétrocompatibilité
        if role.name == 'superuser':
            stats['superusers'] = User.objects.filter(role=role).count()
        elif role.name == 'user':
            stats['regular_users'] = User.objects.filter(role=role).count()
    
    return stats, role_stats
    
    return stats, role_stats

@login_required_custom
def superuser_dashboard_view(request):
    """Tableau de bord administrateur avec statistiques en temps réel"""
    user = request.user_obj
    
    # Vérification du rôle
    if not user.role or user.role.name != 'superuser':
        messages.error(request, 'Accès non autorisé. Droits administrateur requis.')
        return redirect('user_dashboard' if user.role and user.role.name == 'user' else 'login')
    
    try:
        # Récupération des statistiques
        stats, role_stats = get_dashboard_stats()
        
        context = {
            'user': user,
            'page_title': 'Tableau de bord administrateur',
            'stats': stats,
            'role_stats': role_stats,
        }
    except Role.DoesNotExist:
        messages.error(request, 'Erreur de configuration: les rôles par défaut n\'existent pas.')
        return redirect('user_dashboard')
    
    return render(request, 'dashboards/superuser_dashboard.html', context)

@require_GET
@login_required_custom
@superuser_required
def superuser_dashboard_stats_api(request):
    """
    API pour récupérer les statistiques du tableau de bord administrateur en AJAX
    """
    try:
        # Récupération des statistiques
        stats, role_stats = get_dashboard_stats()
        
        # Préparation de la réponse
        response_data = {
            'status': 'success',
            'stats': stats,
            'role_stats': role_stats,
            'timestamp': time.time()
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_protect
@require_POST
@login_required_custom
def update_profile_ajax(request):
    """API pour mettre à jour le profil utilisateur (AJAX)"""
    user = request.user_obj
    
    try:
        # Vérifie si on doit supprimer la photo de profil
        delete_picture = request.POST.get('delete_picture') == 'true'
        
        # Récupère les données du formulaire
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        
        if form.is_valid():
            updated_user = form.save(commit=False)
            
            # Supprime la photo de profil si demandé
            if delete_picture and updated_user.profile_picture:
                # Supprime le fichier du stockage
                updated_user.profile_picture.delete(save=False)
                # Efface la référence au fichier
                updated_user.profile_picture = None
            
            # Sauvegarde les modifications
            updated_user.save()
            
            # Met à jour la session
            request.session['user_email'] = updated_user.email
            
            # Recharge l'utilisateur pour s'assurer d'avoir les dernières données
            updated_user.refresh_from_db()
            
            return JsonResponse({
                'success': True,
                'message': 'Profil mis à jour avec succès',
                'data': {
                    'full_name': updated_user.full_name,
                    'email': updated_user.email,
                    'phone': updated_user.phone or '',
                    'initials': updated_user.get_initials(),
                    'profile_picture_url': updated_user.get_profile_picture_url() or ''
                }
            })
        else:
            # Retourne les erreurs de validation
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = error_list[0]
            
            return JsonResponse({
                'success': False,
                'message': 'Erreur de validation',
                'errors': errors
            }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la mise à jour: {str(e)}'
        }, status=500)

@csrf_protect
@require_POST
@login_required_custom
def delete_profile_picture_ajax(request):
    """API pour supprimer la photo de profil (AJAX)"""
    user = request.user_obj
    
    try:
        user.delete_profile_picture()
        
        return JsonResponse({
            'success': True,
            'message': 'Photo de profil supprimée avec succès',
            'data': {
                'initials': user.get_initials()
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la suppression: {str(e)}'
        }, status=500)


# ============================================================================
# GESTION DES RÔLES
# ============================================================================

@login_required_custom
@superuser_required
def manage_roles_view(request):
    """Page de gestion des rôles"""
    user = request.user_obj
    
    # Récupérer tous les rôles avec le compte d'utilisateurs
    all_roles = Role.objects.annotate(
        user_count=Count('users')
    ).order_by('name')
    
    # Séparer les rôles système et personnalisés
    system_roles = all_roles.filter(name__in=['user', 'superuser'])
    custom_roles = all_roles.exclude(name__in=['user', 'superuser'])
    
    context = {
        'user': user,
        'system_roles': system_roles,
        'custom_roles': custom_roles,
        'page_title': 'Gestion des rôles',
    }
    
    return render(request, 'admin/manage_roles.html', context)


@login_required_custom
@superuser_required
def role_create_view(request):
    """Création d'un nouveau rôle personnalisé"""
    user = request.user_obj
    
    if request.method == 'POST':
        form = RoleManagementForm(request.POST, is_system_role=False)
        
        if form.is_valid():
            try:
                role = form.save(commit=False)
                
                # Si ce rôle est défini comme défaut, désactiver les autres
                if role.is_default:
                    Role.objects.filter(is_default=True).update(is_default=False)
                
                role.save()
                
                messages.success(request, f'Rôle "{role.display_name}" créé avec succès.')
                return redirect('manage_roles')
            except Exception as e:
                messages.error(request, f'Erreur lors de la création: {str(e)}')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = RoleManagementForm(is_system_role=False)
    
    context = {
        'user': user,
        'form': form,
        'is_edit': False,
        'is_system_role': False,
        'page_title': 'Créer un rôle',
    }
    
    return render(request, 'admin/role_form.html', context)


@login_required_custom
@superuser_required
def role_edit_view(request, role_id):
    """Modification d'un rôle existant"""
    user = request.user_obj
    
    try:
        role = Role.objects.get(id=role_id)
    except Role.DoesNotExist:
        messages.error(request, 'Rôle introuvable.')
        return redirect('manage_roles')
    
    # Vérifier si c'est un rôle système
    is_system = role.name in ['user', 'superuser']
    
    if request.method == 'POST':
        form = RoleManagementForm(
            request.POST,
            instance=role,
            is_system_role=is_system
        )
        
        if form.is_valid():
            try:
                updated_role = form.save(commit=False)
                
                # Si ce rôle est défini comme défaut, désactiver les autres
                if updated_role.is_default:
                    Role.objects.filter(is_default=True).exclude(pk=updated_role.pk).update(is_default=False)
                
                updated_role.save()
                
                messages.success(request, f'Rôle "{updated_role.display_name}" modifié avec succès.')
                return redirect('manage_roles')
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification: {str(e)}')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = RoleManagementForm(instance=role, is_system_role=is_system)
    
    context = {
        'user': user,
        'form': form,
        'role': role,
        'is_edit': True,
        'is_system_role': is_system,
        'page_title': f'Modifier {role.display_name}',
    }
    
    return render(request, 'admin/role_form.html', context)


@csrf_protect
@require_POST
@login_required_custom
@superuser_required
def role_delete_view(request, role_id):
    """Suppression d'un rôle personnalisé"""
    user = request.user_obj
    
    try:
        role = Role.objects.get(id=role_id)
        
        # Empêcher la suppression des rôles système
        if role.name in ['user', 'superuser']:
            return JsonResponse({
                'success': False,
                'message': 'Les rôles système ne peuvent pas être supprimés.'
            }, status=400)
        
        # Vérifier si des utilisateurs ont ce rôle
        user_count = role.users.count()
        if user_count > 0:
            return JsonResponse({
                'success': False,
                'message': f'Impossible de supprimer ce rôle. {user_count} utilisateur(s) l\'utilisent encore.'
            }, status=400)
        
        role_name = role.display_name
        role.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Rôle "{role_name}" supprimé avec succès.'
        })
        
    except Role.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Rôle introuvable.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=500)