from django.urls import path
from . import views

urlpatterns = [
    # Pages publiques
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    
    # Dashboards
    path('user-dashboard/', views.user_dashboard_view, name='user_dashboard'),
    path('superuser-dashboard/', views.superuser_dashboard_view, name='superuser_dashboard'),
    
    # Gestion des utilisateurs (admin) - URLs personnalisées
    path('gestion-utilisateurs/', views.user_management_list, name='user_management'),
    path('gestion-utilisateurs/creer/', views.user_create_view, name='user_create'),
    path('gestion-utilisateurs/<int:user_id>/modifier/', views.user_edit_view, name='user_edit'),
    path('gestion-utilisateurs/<int:user_id>/supprimer/', views.user_delete_view, name='user_delete'),
    path('gestion-utilisateurs/<int:user_id>/changer-statut/', views.user_toggle_status_view, name='user_toggle_status'),
    
    # Gestion des rôles (admin)
    path('gestion-roles/', views.manage_roles_view, name='manage_roles'),
    path('gestion-roles/creer/', views.role_create_view, name='role_create'),
    path('gestion-roles/<int:role_id>/modifier/', views.role_edit_view, name='role_edit'),
    path('gestion-roles/<int:role_id>/supprimer/', views.role_delete_view, name='role_delete'),
    
    # Tableaux de bord
    path('role-dashboard/<int:role_id>/', views.role_dashboard_view, name='role_dashboard'),
    
    # API endpoints
    path('api/profile/update/', views.update_profile_ajax, name='api_update_profile'),
    path('api/profile/delete-picture/', views.delete_profile_picture_ajax, name='api_delete_profile_picture'),
    path('api/superuser-dashboard/stats/', views.superuser_dashboard_stats_api, name='api_superuser_dashboard_stats'),
]