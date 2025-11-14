from django import forms
from .models import User, Role
import re
import phonenumbers
from phonenumbers import NumberParseException
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
import io

class SignupForm(forms.ModelForm):
    """Formulaire d'inscription avec validations avancées"""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
            'placeholder': 'Mot de passe',
            'id': 'password'
        }),
        label="Mot de passe"
    )
    
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
            'placeholder': 'Confirmer le mot de passe',
            'id': 'password_confirm'
        }),
        label="Confirmation du mot de passe"
    )
    
    country_code = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'country_code'}),
        required=False,
        initial='+229'  # Bénin par défaut
    )
    
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
            'placeholder': '90 00 00 00',
            'id': 'phone_number'
        }),
        label="Numéro de téléphone"
    )
    
    accept_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500',
            'id': 'accept_terms'
        }),
        error_messages={'required': 'Vous devez accepter les conditions d\'utilisation'}
    )
    
    class Meta:
        model = User
        fields = ['full_name', 'email']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
                'placeholder': 'Nom Prénom(s)',
                'id': 'full_name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
                'placeholder': 'exemple@email.com',
                'id': 'email'
            }),
        }
        labels = {
            'full_name': 'Nom complet',
            'email': 'Adresse e-mail'
        }
    
    def clean_full_name(self):
        """Valide le format du nom complet"""
        full_name = self.cleaned_data.get('full_name', '').strip()
        
        # Protection XSS
        full_name = re.sub(r'[<>\"\'&]', '', full_name)
        
        is_valid, normalized_name = User.validate_full_name(full_name)
        
        if not is_valid:
            raise forms.ValidationError(
                'Format invalide. Utilisez: "Nom Prénom", "Nom_Prénom" ou "NomPrénom" (minimum 2 segments)'
            )
        
        return normalized_name
    
    def clean_email(self):
        """Valide et normalise l'email"""
        email = self.cleaned_data.get('email', '').lower().strip()
        
        # Validation RFC 5322 basique
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise forms.ValidationError('Format d\'adresse e-mail invalide')
        
        # Vérification d'unicité
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Cette adresse e-mail est déjà utilisée')
        
        # Protection contre emails jetables (liste basique)
        disposable_domains = [
            'tempmail.com', 'throwaway.email', '10minutemail.com',
            'guerrillamail.com', 'mailinator.com', 'trashmail.com'
        ]
        domain = email.split('@')[1]
        if domain in disposable_domains:
            raise forms.ValidationError('Les adresses e-mail jetables ne sont pas autorisées')
        
        return email
    
    def clean_phone_number(self):
        """Valide le numéro de téléphone"""
        phone_number = self.cleaned_data.get('phone_number', '').strip()
        country_code = self.data.get('country_code', '+229')
        
        # Construit le numéro complet
        full_number = country_code + re.sub(r'[\s\-\(\)]', '', phone_number)
        
        try:
            parsed_number = phonenumbers.parse(full_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise forms.ValidationError('Numéro de téléphone invalide pour ce pays')
            
            # Format international
            formatted_number = phonenumbers.format_number(
                parsed_number,
                phonenumbers.PhoneNumberFormat.E164
            )
            
            # Vérification d'unicité
            if User.objects.filter(phone=formatted_number).exists():
                raise forms.ValidationError('Ce numéro de téléphone est déjà utilisé')
            
            return formatted_number
            
        except NumberParseException:
            raise forms.ValidationError('Format de numéro de téléphone invalide')
    
    def clean_password(self):
        """Valide la robustesse du mot de passe"""
        password = self.cleaned_data.get('password', '')
        
        if len(password) < 8:
            raise forms.ValidationError('Le mot de passe doit contenir au moins 8 caractères')
        
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('Le mot de passe doit contenir au moins une majuscule')
        
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError('Le mot de passe doit contenir au moins une minuscule')
        
        if not re.search(r'\d', password):
            raise forms.ValidationError('Le mot de passe doit contenir au moins un chiffre')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError('Le mot de passe doit contenir au moins un caractère spécial')
        
        # Vérification contre données personnelles (si disponibles)
        if hasattr(self, 'cleaned_data'):
            full_name = self.cleaned_data.get('full_name', '')
            email = self.cleaned_data.get('email', '')
            
            name_parts = re.split(r'[\s_]|(?=[A-Z])', full_name.lower())
            for part in name_parts:
                if part and len(part) > 2 and part in password.lower():
                    raise forms.ValidationError('Le mot de passe ne doit pas contenir votre nom')
            
            email_local = email.split('@')[0].lower()
            if email_local in password.lower():
                raise forms.ValidationError('Le mot de passe ne doit pas contenir votre adresse e-mail')
        
        return password
    
    def clean(self):
        """Validation finale et cohérence des mots de passe"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Les mots de passe ne correspondent pas')
        
        # Combine country_code et phone_number pour le champ phone du modèle
        phone_number = cleaned_data.get('phone_number')
        if phone_number:
            cleaned_data['phone'] = phone_number
        
        return cleaned_data

class LoginForm(forms.Form):
    """Formulaire de connexion sécurisé avec validations"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
            'placeholder': 'exemple@email.com',
            'id': 'email',
            'autocomplete': 'email'
        }),
        label="Adresse e-mail",
        error_messages={
            'required': 'L\'adresse e-mail est obligatoire',
            'invalid': 'Veuillez entrer une adresse e-mail valide'
        }
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all',
            'placeholder': 'Mot de passe',
            'id': 'password',
            'autocomplete': 'current-password'
        }),
        label="Mot de passe",
        error_messages={
            'required': 'Le mot de passe est obligatoire'
        }
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500',
            'id': 'remember_me'
        }),
        label="Se souvenir de moi"
    )
    
    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super().__init__(*args, **kwargs)
    
    def clean_email(self):
        """Normalise l'email"""
        email = self.cleaned_data.get('email', '').lower().strip()
        
        # Protection XSS basique
        email = re.sub(r'[<>\"\'&]', '', email)
        
        return email
    
    def clean(self):
        """Valide les identifiants"""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            # Recherche de l'utilisateur par email avec select_related pour charger le rôle
            try:
                from .models import User
                user = User.objects.select_related('role').get(email=email)
                
                # Vérification du mot de passe
                if not user.check_password(password):
                    raise ValidationError(
                        'Identifiants incorrects. Veuillez vérifier votre email et mot de passe.',
                        code='invalid_login'
                    )
                
                # Vérification que l'utilisateur est actif
                if not user.is_active:
                    raise ValidationError(
                        'Ce compte est désactivé. Veuillez contacter un administrateur.',
                        code='inactive_account'
                    )
                
                # Stockage de l'utilisateur pour utilisation dans la vue
                self.user_cache = user
                
            except User.DoesNotExist:
                raise ValidationError(
                    'Identifiants incorrects. Veuillez vérifier votre email et mot de passe.',
                    code='invalid_login'
                )
        
        return cleaned_data
    
    def get_user(self):
        """Retourne l'utilisateur authentifié"""
        return self.user_cache

class ProfileUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour du profil utilisateur"""
    
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'profile_picture']
    
    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        
        # Rend l'email unique sauf pour l'utilisateur actuel
        if self.user_instance:
            self.fields['email'].required = True
            self.fields['phone'].required = True
    
    def clean_profile_picture(self):
        """Valide et optimise la photo de profil"""
        picture = self.cleaned_data.get('profile_picture')
        
        if picture and hasattr(picture, 'size'):
            # Limite de taille : 5MB
            if picture.size > 5 * 1024 * 1024:
                raise forms.ValidationError('La taille de l\'image ne doit pas dépasser 5MB')
            
            # Vérifie que c'est bien une image
            try:
                img = Image.open(picture)
                img.verify()
                
                # Réouvre l'image pour la manipulation
                picture.seek(0)
                img = Image.open(picture)
                
                # Optimise l'image (redimensionne si trop grande)
                max_size = (800, 800)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Sauvegarde l'image optimisée
                    output = io.BytesIO()
                    img_format = img.format if img.format else 'JPEG'
                    img.save(output, format=img_format, quality=85, optimize=True)
                    output.seek(0)
                    
                    picture = InMemoryUploadedFile(
                        output,
                        'ImageField',
                        picture.name,
                        f'image/{img_format.lower()}',
                        output.getbuffer().nbytes,
                        None
                    )
            
            except Exception as e:
                raise forms.ValidationError('Fichier image invalide')
        
        return picture
    
    def clean_full_name(self):
        """Valide le format du nom complet"""
        full_name = self.cleaned_data.get('full_name', '').strip()
        full_name = re.sub(r'[<>\"\'&]', '', full_name)
        
        is_valid, normalized_name = User.validate_full_name(full_name)
        
        if not is_valid:
            raise forms.ValidationError(
                'Format invalide. Utilisez: "Nom Prénom", "Nom_Prénom" ou "NomPrénom"'
            )
        
        return normalized_name
    
    def clean_email(self):
        """Valide et normalise l'email"""
        email = self.cleaned_data.get('email', '').lower().strip()
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise forms.ValidationError('Format d\'adresse e-mail invalide')
        
        # Vérification d'unicité (exclut l'utilisateur actuel)
        if self.user_instance:
            if User.objects.filter(email=email).exclude(id=self.user_instance.id).exists():
                raise forms.ValidationError('Cette adresse e-mail est déjà utilisée')
        
        return email
    
    def clean_phone(self):
        """Valide le numéro de téléphone"""
        phone = self.cleaned_data.get('phone', '').strip()
        
        # Vérification d'unicité (exclut l'utilisateur actuel)
        if self.user_instance:
            if User.objects.filter(phone=phone).exclude(id=self.user_instance.id).exists():
                raise forms.ValidationError('Ce numéro de téléphone est déjà utilisé')
        
        return phone

class UserManagementForm(forms.ModelForm):
    """Formulaire de gestion des utilisateurs (création/édition par admin)"""
    
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            'placeholder': 'Nouveau mot de passe (laisser vide pour ne pas modifier)',
        }),
        label="Mot de passe",
        help_text="Minimum 8 caractères. Laisser vide pour ne pas modifier."
    )
    
    password_confirm = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
            'placeholder': 'Confirmer le mot de passe',
        }),
        label="Confirmation du mot de passe"
    )
    
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'role', 'is_active', 'profile_picture']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
                'placeholder': 'Nom Prénom(s)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
                'placeholder': 'email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
                'placeholder': '+229 90 00 00 00'
            }),
            'role': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-2 focus:ring-purple-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)
        
        if self.is_edit:
            # En mode édition, le mot de passe n'est pas obligatoire
            self.fields['password'].required = False
            self.fields['password_confirm'].required = False
        else:
            # En mode création, le mot de passe est obligatoire
            self.fields['password'].required = True
            self.fields['password_confirm'].required = True
    
    def clean_full_name(self):
        """Valide le format du nom complet"""
        full_name = self.cleaned_data.get('full_name', '').strip()
        full_name = re.sub(r'[<>\"\'&]', '', full_name)
        
        is_valid, normalized_name = User.validate_full_name(full_name)
        
        if not is_valid:
            raise forms.ValidationError(
                'Format invalide. Utilisez: "Nom Prénom", "Nom_Prénom" ou "NomPrénom"'
            )
        
        return normalized_name
    
    def clean_email(self):
        """Valide et normalise l'email"""
        email = self.cleaned_data.get('email', '').lower().strip()
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise forms.ValidationError('Format d\'adresse e-mail invalide')
        
        # Vérification d'unicité (exclut l'instance actuelle si édition)
        if self.instance and self.instance.pk:
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Cette adresse e-mail est déjà utilisée')
        else:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('Cette adresse e-mail est déjà utilisée')
        
        return email
    
    def clean_phone(self):
        """Valide le numéro de téléphone"""
        phone = self.cleaned_data.get('phone', '').strip()
        
        # Vérification d'unicité (exclut l'instance actuelle si édition)
        if self.instance and self.instance.pk:
            if User.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Ce numéro de téléphone est déjà utilisé')
        else:
            if User.objects.filter(phone=phone).exists():
                raise forms.ValidationError('Ce numéro de téléphone est déjà utilisé')
        
        return phone
    
    def clean(self):
        """Validation globale"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        # Valide le mot de passe si fourni
        if password or password_confirm:
            if password != password_confirm:
                raise forms.ValidationError('Les mots de passe ne correspondent pas')
            
            if password and len(password) < 8:
                raise forms.ValidationError('Le mot de passe doit contenir au moins 8 caractères')
        
        # En mode création, le mot de passe est obligatoire
        if not self.is_edit and not password:
            raise forms.ValidationError('Le mot de passe est obligatoire pour créer un utilisateur')
        
        return cleaned_data
    
    def save(self, commit=True):
        """Sauvegarde avec hashage du mot de passe"""
        user = super().save(commit=False)
        
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
        
        return user

# ============================================================================
# FORMULAIRE DE GESTION DES RÔLES
# ============================================================================

class RoleManagementForm(forms.ModelForm):
    """Formulaire de création et modification de rôles"""
    
    class Meta:
        model = Role
        fields = ['name', 'display_name']  # Suppression de is_default des champs par défaut
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
                'placeholder': 'ex: manager, editor, viewer',
                'id': 'role_name'
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all',
                'placeholder': 'ex: Gestionnaire, Éditeur, Observateur',
                'id': 'role_display_name'
            }),
        }
        labels = {
            'name': 'Nom technique du rôle',
            'display_name': 'Nom d\'affichage',
        }
        help_texts = {
            'name': 'En minuscules, sans espaces (ex: editor, manager)',
            'display_name': 'Nom convivial affiché dans l\'interface',
        }
    
    def __init__(self, *args, **kwargs):
        self.is_system_role = kwargs.pop('is_system_role', False)
        super().__init__(*args, **kwargs)
        
        # Si c'est un rôle système, le nom ne peut pas être modifié
        if self.is_system_role and self.instance.pk:
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['name'].help_text = '⚠️ Le nom des rôles système ne peut pas être modifié'
        
        # Ajout d'un champ caché pour le rôle user qui forcera is_default à True
        if self.instance and self.instance.name == 'user':
            self.fields['is_default'] = forms.BooleanField(
                initial=True,
                required=False,
                widget=forms.HiddenInput()
            )
            # Ajout d'un champ visuel en lecture seule pour indiquer que c'est le rôle par défaut
            self.fields['default_role_info'] = forms.CharField(
                initial='✅ Ce rôle est le rôle par défaut du système',
                required=False,
                disabled=True,
                widget=forms.TextInput(attrs={
                    'class': 'w-full px-4 py-3 border-0 bg-gray-50 text-gray-700',
                    'readonly': 'readonly'
                })
            )
            
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Force is_default à True pour le rôle user
        if hasattr(instance, 'name') and instance.name == 'user':
            instance.is_default = True
        
        if commit:
            instance.save()
        return instance
    
    def clean_name(self):
        """Valide le nom du rôle"""
        name = self.cleaned_data.get('name', '').strip().lower()
        
        # Protection XSS
        name = re.sub(r'[<>\"\'&]', '', name)
        
        # Validation du format (lettres, chiffres, underscore uniquement)
        if not re.match(r'^[a-z0-9_]+$', name):
            raise forms.ValidationError(
                'Le nom doit contenir uniquement des lettres minuscules, chiffres et underscores'
            )
        
        # Vérification de longueur
        if len(name) < 2:
            raise forms.ValidationError('Le nom doit contenir au moins 2 caractères')
        
        if len(name) > 50:
            raise forms.ValidationError('Le nom ne doit pas dépasser 50 caractères')
        
        # Empêcher la création de rôles avec des noms système
        if not self.instance.pk and name in ['user', 'superuser']:
            raise forms.ValidationError('Ce nom est réservé aux rôles système')
        
        # Vérification d'unicité (sauf pour l'instance courante)
        if self.instance.pk:
            if Role.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Un rôle avec ce nom existe déjà')
        else:
            if Role.objects.filter(name=name).exists():
                raise forms.ValidationError('Un rôle avec ce nom existe déjà')
        
        return name
    
    def clean_display_name(self):
        """Valide le nom d'affichage"""
        display_name = self.cleaned_data.get('display_name', '').strip()
        
        # Protection XSS
        display_name = re.sub(r'[<>\"\'&]', '', display_name)
        
        if len(display_name) < 2:
            raise forms.ValidationError('Le nom d\'affichage doit contenir au moins 2 caractères')
        
        if len(display_name) > 100:
            raise forms.ValidationError('Le nom d\'affichage ne doit pas dépasser 100 caractères')
        
        return display_name
    
    def clean_is_default(self):
        """Valide le champ is_default"""
        is_default = self.cleaned_data.get('is_default', False)
        
        # Le rôle superuser ne peut jamais être le rôle par défaut
        if is_default and self.instance.pk and self.instance.name == 'superuser':
            raise forms.ValidationError('Le rôle superuser ne peut pas être le rôle par défaut')
        
        return is_default
    
    def clean(self):
        """Validation globale"""
        cleaned_data = super().clean()
        is_default = cleaned_data.get('is_default', False)
        
        # Si on définit ce rôle comme défaut, désactiver les autres
        if is_default:
            # Cette logique sera gérée dans la vue pour éviter les conflits
            pass
        
        return cleaned_data