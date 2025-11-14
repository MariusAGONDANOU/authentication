from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
import re
import os
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError

def user_profile_picture_path(instance, filename):
    """Chemin de stockage des photos de profil"""
    ext = filename.split('.')[-1]
    filename = f'user_{instance.id}_profile.{ext}'
    return os.path.join('profile_pictures', filename)


class UserManager(BaseUserManager):
    """Manager personnalisé pour le modèle User"""
    
    def create_user(self, email, full_name, phone, password=None, **extra_fields):
        """Crée et sauvegarde un utilisateur standard"""
        if not email:
            raise ValueError('L\'adresse email est obligatoire')
        
        email = self.normalize_email(email)
        role_name = extra_fields.pop('role', 'user')
        
        user = self.model(
            email=email,
            full_name=full_name,
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, full_name, phone, password=None, **extra_fields):
        """
        Crée et sauvegarde un superutilisateur avec le rôle 'superuser'.
        """
        from .models import Role
        
        # S'assurer que le rôle 'superuser' existe
        role, created = Role.objects.get_or_create(
            name='superuser',
            defaults={
                'display_name': 'Super Utilisateur',
                'is_default': False
            }
        )
        
        # Définir les attributs de superutilisateur
        extra_fields.update({
            'role': role,
            'is_staff': True,
            'is_superuser': True
        })
        
        # Créer l'utilisateur avec tous les attributs
        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            phone=phone,
            **extra_fields
        )
        
        user.set_password(password)
        user.save(using=self._db)
        
        return user


class Role(models.Model):
    """Modèle pour gérer les rôles personnalisés"""
    name = models.CharField(
        _('nom du rôle'),
        max_length=50,
        unique=True,
        help_text=_('Nom unique du rôle (en minuscules, sans espaces, ex: editor, manager)')
    )
    display_name = models.CharField(
        _('nom d\'affichage'),
        max_length=100,
        help_text=_('Nom affiché dans l\'interface')
    )
    is_default = models.BooleanField(
        _('rôle par défaut'),
        default=False,
        help_text=_('Si coché, ce rôle sera attribué par défaut aux nouveaux utilisateurs')
    )
    permissions = models.JSONField(
        _('permissions'),
        default=dict,
        blank=True,
        help_text=_('Dictionnaire JSON des permissions spécifiques au rôle')
    )
    created_at = models.DateTimeField(_('date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('date de modification'), auto_now=True)

    class Meta:
        verbose_name = _('rôle')
        verbose_name_plural = _('rôles')
        ordering = ['name']

    def __str__(self):
        return self.display_name

    def clean(self):
        # S'assurer qu'il n'y a qu'un seul rôle par défaut
        if self.is_default:
            Role.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)

    def save(self, *args, **kwargs):
        # S'assurer que le nom est en minuscules et sans espaces
        self.name = self.name.lower().strip().replace(' ', '_')
        super().save(*args, **kwargs)
        
    def __json__(self):
        """Sérialisation JSON personnalisée pour le modèle Role"""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'is_default': self.is_default,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

def is_system_role(self):
    """Vérifie si le rôle est un rôle système (non supprimable)"""
    return self.name in ['user', 'superuser']

def user_count(self):
    """Retourne le nombre d'utilisateurs ayant ce rôle"""
    return self.users.count()

@classmethod
def get_system_roles(cls):
    """Retourne les rôles système"""
    return cls.objects.filter(name__in=['user', 'superuser'])

@classmethod
def get_custom_roles(cls):
    """Retourne les rôles personnalisés (non-système)"""
    return cls.objects.exclude(name__in=['user', 'superuser'])

class User(AbstractBaseUser, PermissionsMixin):
    """Modèle utilisateur personnalisé avec validation complète"""
    
    # Rôles système prédéfinis
    SYSTEM_ROLES = {
        'superuser': 'Super Utilisateur',
        'user': 'Utilisateur',
    }
    
    full_name = models.CharField(
        max_length=255,
        verbose_name="Nom complet",
        help_text="Format: Nom Prénom(s) ou Nom_Prénom(s) ou NomPrénom(s)"
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Adresse e-mail",
        db_index=True
    )
    
    # Champs requis pour le modèle utilisateur personnalisé
    is_staff = models.BooleanField(
        default=False,
        help_text='Détermine si l\'utilisateur peut se connecter à l\'interface d\'administration.',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Désigne si cet utilisateur doit être considéré comme actif. Désélectionnez ceci plutôt que de supprimer le compte.',
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date d'inscription"
    )
    phone = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Numéro de téléphone",
        db_index=True
    )
    password = models.CharField(
        max_length=255,
        verbose_name="Mot de passe"
    )
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path,
        null=True,
        blank=True,
        verbose_name="Photo de profil",
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']
            )
        ],
        help_text="Formats acceptés: JPG, JPEG, PNG, GIF, WEBP. Taille max: 5MB"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        verbose_name=_('rôle'),
        related_name='users',
        null=True,
        blank=True,
        help_text=_('Rôle de l\'utilisateur dans le système')
    )
    # is_active est maintenant défini plus haut avec plus d'options
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    objects = UserManager()
    
    # Champs requis pour compatibilité avec Django Admin
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-created_at']
        permissions = [
            ("can_manage_users", "Peut gérer les utilisateurs"),
            ("can_view_dashboard", "Peut voir le dashboard"),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def set_password(self, raw_password):
        """Hash le mot de passe avant sauvegarde"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Vérifie si le mot de passe correspond"""
        return check_password(raw_password, self.password)
    
    def get_initials(self):
        """Génère les initiales à partir du nom complet"""
        # Nettoyer et diviser le nom complet
        parts = [p for p in re.split(r'[\s_]+', self.full_name.strip()) if p]
        
        # Si le nom complet est au format "Nom Prenom1 Prenom2"
        if len(parts) == 3 and all(part[0].isupper() for part in parts):
            return ''.join(part[0] for part in parts).upper()
        
        # Gestion des autres formats de noms
        if len(parts) >= 2:
            # Pour les noms avec prénoms multiples, on prend la première lettre de chaque partie
            return ''.join(part[0].upper() for part in parts[:3] if part)
        elif parts:
            # Si une seule partie, on prend les deux premiers caractères
            return parts[0][:2].upper()
        
        # Par défaut, retourner les deux premières lettres de l'email
        return self.email[:2].upper() if self.email else 'US'
    
    def has_profile_picture(self):
        """Vérifie si l'utilisateur a une photo de profil"""
        return bool(self.profile_picture and self.profile_picture.name)
    
    def get_profile_picture_url(self):
        """Retourne l'URL de la photo de profil ou None"""
        if self.has_profile_picture():
            try:
                return self.profile_picture.url
            except ValueError:
                return None
        return None
    
    def get_profile_picture_url_safe(self):
        """Alias pour get_profile_picture_url (compatibilité)"""
        return self.get_profile_picture_url()
    
    @property
    def is_superuser(self):
        """Vérifie si l'utilisateur est un superuser"""
        if hasattr(self, '_is_superuser'):
            return self._is_superuser
        return self.role and self.role.name == 'superuser'
        
    @is_superuser.setter
    def is_superuser(self, value):
        """Définit si l'utilisateur est un superuser"""
        self._is_superuser = value
    
    @property
    def is_staff(self):
        """Vérifie si l'utilisateur est staff (pour Django Admin)"""
        if hasattr(self, '_is_staff'):
            return self._is_staff
        return self.is_superuser  # Seuls les superusers ont accès à l'admin Django
        
    @is_staff.setter
    def is_staff(self, value):
        """Définit si l'utilisateur est staff"""
        self._is_staff = value
    
    def has_perm(self, perm, obj=None):
        """Vérifie si l'utilisateur a une permission spécifique"""
        if self.is_superuser:
            return True
            
        if not self.role:
            return False
            
        # Vérifier les permissions personnalisées du rôle
        if isinstance(self.role.permissions, dict):
            # Gestion des permissions hiérarchiques (ex: 'app.view_model')
            parts = perm.split('.')
            for i in range(len(parts), 0, -1):
                check_perm = '.'.join(parts[:i])
                if check_perm in self.role.permissions.get('permissions', []):
                    return True
                    
        return super().has_perm(perm, obj)
    
    def has_module_perms(self, app_label):
        """Vérifie si l'utilisateur a des permissions pour une application"""
        if self.is_superuser:
            return True
            
        if not self.role:
            return False
            
        # Vérifier les permissions d'application du rôle
        if isinstance(self.role.permissions, dict):
            app_perms = self.role.permissions.get('app_permissions', [])
            if app_label in app_perms:
                return True
                
        return super().has_module_perms(app_label)
    
    def get_role_display(self):
        """Retourne le nom d'affichage du rôle"""
        if self.role:
            return self.role.display_name
        return _('Aucun rôle')
    
    @classmethod
    def get_default_role(cls):
        """Retourne le rôle par défaut"""
        try:
            return Role.objects.get(is_default=True)
        except (Role.DoesNotExist, Role.MultipleObjectsReturned):
            # En cas d'erreur, on essaie de récupérer le rôle 'user'
            try:
                return Role.objects.get(name='user')
            except (Role.DoesNotExist, Role.MultipleObjectsReturned):
                # Si aucun rôle n'existe, on en crée un par défaut
                return Role.objects.create(
                    name='user',
                    display_name='Utilisateur',
                    is_default=True
                )
    
    @staticmethod
    def validate_full_name(name):
        """Valide le format du nom complet"""
        name = re.sub(r'\s+', ' ', name.strip())
        
        patterns = [
            r'^[A-Za-zÀ-ÿ]+[\s_][A-Za-zÀ-ÿ]+[\s_]*[A-Za-zÀ-ÿ]*$',
            r'^[A-Z][a-z]+[A-Z][a-z]+[A-Z]*[a-z]*$',
        ]
        
        for pattern in patterns:
            if re.match(pattern, name):
                segments = re.split(r'[\s_]|(?=[A-Z])', name)
                segments = [s for s in segments if s]
                if len(segments) >= 2:
                    return True, name
        
        return False, None
    
    def save(self, *args, **kwargs):
        # S'assurer que l'email est en minuscules
        self.email = self.email.lower()
        
        # Attribuer un rôle par défaut si aucun n'est défini
        if not self.role and not self.pk:
            self.role = self.get_default_role()
            
        super().save(*args, **kwargs)
    
    def delete_profile_picture(self):
        """Supprime la photo de profil actuelle"""
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)
            self.profile_picture = None
            self.save()
