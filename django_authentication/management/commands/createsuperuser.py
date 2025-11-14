from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django_authentication.models import User
import getpass
import re

class Command(BaseCommand):
    help = 'Crée un superutilisateur avec role="superuser"'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Adresse email')
        parser.add_argument('--full-name', type=str, help='Nom complet')
        parser.add_argument('--phone', type=str, help='Numéro de téléphone')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Création d\'un superutilisateur ===\n'))

        # Récupérer l'email
        email = options.get('email')
        while not email:
            email = input('Adresse e-mail: ').strip().lower()
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                self.stdout.write(self.style.ERROR('Format d\'email invalide'))
                email = None
            elif User.objects.filter(email=email).exists():
                self.stdout.write(self.style.ERROR('Cet email existe déjà'))
                email = None

        # Récupérer le nom complet
        full_name = options.get('full_name')
        while not full_name:
            full_name = input('Nom complet (ex: Dupont Jean): ').strip()
            is_valid, normalized = User.validate_full_name(full_name)
            if not is_valid:
                self.stdout.write(self.style.ERROR('Format de nom invalide'))
                full_name = None
            else:
                full_name = normalized

        # Récupérer le téléphone
        phone = options.get('phone')
        while not phone:
            phone = input('Numéro de téléphone: ').strip()
            if User.objects.filter(phone=phone).exists():
                self.stdout.write(self.style.ERROR('Ce numéro existe déjà'))
                phone = None

        # Récupérer le mot de passe
        password = None
        while not password:
            password = getpass.getpass('Mot de passe: ')
            password_confirm = getpass.getpass('Confirmer le mot de passe: ')
            
            if password != password_confirm:
                self.stdout.write(self.style.ERROR('Les mots de passe ne correspondent pas'))
                password = None
                continue
            
            if len(password) < 8:
                self.stdout.write(self.style.ERROR('Le mot de passe doit contenir au moins 8 caractères'))
                password = None

        try:
            # Créer le superuser
            user = User.objects.create_superuser(
                email=email,
                full_name=full_name,
                phone=phone,
                password=password
            )
            
            self.stdout.write(self.style.SUCCESS(f'\n✓ Superutilisateur créé avec succès!'))
            self.stdout.write(self.style.SUCCESS(f'  Email: {user.email}'))
            self.stdout.write(self.style.SUCCESS(f'  Rôle: {user.role}'))
            self.stdout.write(self.style.SUCCESS(f'  ID: {user.id}\n'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Erreur: {str(e)}\n'))

