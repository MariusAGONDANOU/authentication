from django import template
from django.templatetags.static import static

register = template.Library()

@register.filter(name='has_profile_picture')
def has_profile_picture(user):
    """Vérifie si l'utilisateur a une photo de profil"""
    if not user or not hasattr(user, 'profile_picture'):
        return False
    
    # Vérifie si le fichier existe réellement
    try:
        return bool(user.profile_picture and user.profile_picture.name)
    except (ValueError, AttributeError):
        return False

@register.simple_tag
def profile_picture_url(user):
    """Retourne l'URL de la photo de profil ou une URL par défaut"""
    # Vérifie d'abord si la méthode get_profile_picture_url_safe existe
    if hasattr(user, 'get_profile_picture_url_safe'):
        try:
            url = user.get_profile_picture_url_safe()
            if url:
                return url
        except (ValueError, AttributeError):
            pass
    
    # Sinon, essaie d'accéder directement au champ profile_picture
    if hasattr(user, 'profile_picture'):
        try:
            if user.profile_picture and user.profile_picture.name:
                return user.profile_picture.url
        except (ValueError, AttributeError):
            pass
    
    # Si tout échoue, retourne l'image par défaut
    return static('images/default-avatar.svg')
