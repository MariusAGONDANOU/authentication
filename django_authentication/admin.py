from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import (
    UserChangeForm as BaseUserChangeForm,
    UserCreationForm as BaseUserCreationForm
)

from .models import User, Role

class RoleAdminForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        is_default = cleaned_data.get('is_default')
        
        # Si on essaie de définir ce rôle comme rôle par défaut
        if is_default:
            # Vérifier si un autre rôle est déjà défini comme rôle par défaut
            existing_default = Role.objects.filter(is_default=True).exclude(pk=self.instance.pk if self.instance else None)
            if existing_default.exists():
                # Si un autre rôle est déjà défini comme rôle par défaut, le déselectionner
                existing_default.update(is_default=False)
        
        return cleaned_data


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Administration du modèle Role"""
    form = RoleAdminForm
    list_display = ('name', 'display_name', 'is_default', 'user_count', 'created_at')
    list_filter = ('is_default', 'created_at')
    search_fields = ('name', 'display_name')
    readonly_fields = ('created_at', 'updated_at', 'user_count_display')
    fieldsets = (
        (None, {
            'fields': ('name', 'display_name', 'is_default', 'permissions')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'user_count_display'),
            'classes': ('collapse',)
        }),
    )
    
    def user_count_display(self, obj):
        return obj.users.count()
    user_count_display.short_description = _("Nombre d'utilisateurs")
    
    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = _('Utilisateurs')
    
    def get_readonly_fields(self, request, obj=None):
        # Ne pas permettre la modification du nom du rôle système
        if obj and obj.name in ['user', 'superuser']:
            return self.readonly_fields + ('name', 'is_default')
        return self.readonly_fields
    
    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression des rôles système
        if obj and obj.name in ['user', 'superuser']:
            return False
        return super().has_delete_permission(request, obj)


class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
        return email


class UserChangeForm(BaseUserChangeForm):
    class Meta:
        model = User
        fields = '__all__'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
        return email


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administration du modèle User"""
    
    form = UserChangeForm
    add_form = UserCreationForm
    
    list_display = ('email', 'full_name', 'phone', 'role_display', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('email', 'full_name', 'phone')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login', 'created_at', 'updated_at')
    filter_horizontal = ('user_permissions', 'groups')
    
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Informations personnelles'), {
            'fields': ('full_name', 'phone', 'profile_picture')
        }),
        (_('Rôle et permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'groups', 'user_permissions')
        }),
        (_('Dates importantes'), {
            'fields': ('date_joined', 'last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'phone', 'password1', 'password2', 'role'),
        }),
    )
    
    def role_display(self, obj):
        return obj.get_role_display()
    role_display.short_description = _('Rôle')
    role_display.admin_order_field = 'role__name'
    
    def get_readonly_fields(self, request, obj=None):
        # Ne pas permettre la modification du rôle superuser
        if obj and obj.is_superuser() and not request.user.is_superuser():
            return self.readonly_fields + ('role', 'is_staff', 'is_active')
        return self.readonly_fields
    
    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression de l'utilisateur superuser
        if obj and obj.is_superuser() and not request.user.is_superuser():
            return False
        return super().has_delete_permission(request, obj)
    
    def save_model(self, request, obj, form, change):
        # Si c'est un nouvel utilisateur et qu'aucun rôle n'est défini, utiliser le rôle par défaut
        if not change and not obj.role:
            obj.role = User.get_default_role()
        
        # Si le mot de passe a été modifié, le hasher
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        
        super().save_model(request, obj, form, change)
    
    def response_add(self, request, obj, post_url_continue=None):
        """Rediriger vers la page d'édition après l'ajout d'un utilisateur"""
        if '_addanother' in request.POST:
            return super().response_add(request, obj, post_url_continue)
        return HttpResponseRedirect(reverse('admin:django_authentication_user_changelist'))
    
    def get_actions(self, request):
        """Désactiver la suppression en masse pour les utilisateurs non superusers"""
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions
