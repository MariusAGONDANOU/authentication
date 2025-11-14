from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

# URLs personnalisées pour l'administration
admin_site_urls = [
    # Inclure d'abord les URLs personnalisées
    path('users/', include('django_authentication.urls')),
    # Puis les URLs de l'admin standard
    path('', admin.site.urls),
]

urlpatterns = [
    # URLs de l'administration avec nos personnalisations
    path('admin/', include(admin_site_urls)),
    # Autres URLs de l'application
    path('', include('django_authentication.urls')),
]

# Servir les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

