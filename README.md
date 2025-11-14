# Système d'Authentification Django

Un système d'authentification complet construit avec Django, offrant des fonctionnalités d'inscription, de connexion, de réinitialisation de mot de passe et de gestion de profil utilisateur.

## 📋 Fonctionnalités

- Inscription des utilisateurs avec email et mot de passe
- Connexion et déconnexion des utilisateurs
- Réinitialisation du mot de passe par email
- Tableau de bord utilisateur personnalisé
- Gestion des rôles et permissions
- Téléchargement et mise à jour de la photo de profil
- Interface utilisateur moderne et réactive

## 🚀 Prérequis

- Python 3.8+
- Django 4.0+
- PostgreSQL (recommandé) ou SQLite
- Node.js et npm (pour les assets statiques)

## 🛠 Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/MariusAGONDANOU/authentication.git
   cd authentication
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Linux/Mac
   # OU
   .\venv\Scripts\activate  # Sur Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**
   Créez un fichier `.env` à la racine du projet avec les variables nécessaires :
   ```
   SECRET_KEY=votre_secret_key_django
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=sqlite:///db.sqlite3
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
   ```

5. **Appliquer les migrations**
   ```bash
   python manage.py migrate
   ```

6. **Créer un superutilisateur**
   ```bash
   python manage.py createsuperuser
   ```

7. **Lancer le serveur de développement**
   ```bash
   python manage.py runserver
   ```

## 🌐 Accès

- **Interface d'administration** : http://127.0.0.1:8000/admin/
- **Tableau de bord** : http://127.0.0.1:8000/dashboard/
- **API** : http://127.0.0.1:8000/api/

## 📂 Structure du projet

```
authentication/
├── django_authentication/     # Application principale
│   ├── templates/            # Templates HTML
│   ├── static/               # Fichiers statiques (CSS, JS, images)
│   ├── models.py             # Modèles de données
│   ├── views.py              # Vues de l'application
│   └── urls.py               # URLs de l'application
├── authentication/           # Configuration du projet Django
├── media/                    # Fichiers téléchargés par les utilisateurs
├── staticfiles/              # Fichiers statiques collectés
└── manage.py                # Script de gestion de Django
```

## 🔒 Sécurité

- Mots de passe hachés avec PBKDF2
- Protection CSRF activée
- Sécurisation des vues avec décorateurs d'authentification
- Validation des entrées utilisateur

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

1. Forkez le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.

## 📧 Contact

Marius AGONDANOU - [@votre_handle_twitter](https://twitter.com/votre_handle) - email@example.com

Lien du projet : [https://github.com/MariusAGONDANOU/authentication](https://github.com/MariusAGONDANOU/authentication)
