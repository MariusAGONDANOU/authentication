import json
from datetime import datetime
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

class CustomJSONEncoder(DjangoJSONEncoder):
    """Sérialiseur JSON personnalisé pour gérer les objets Django"""
    def default(self, obj):
        # Si l'objet a une méthode __json__, l'utiliser
        if hasattr(obj, '__json__'):
            return obj.__json__()
        # Gérer les champs datetime
        elif isinstance(obj, datetime):
            return obj.isoformat()
        # Gérer les modèles Django
        elif isinstance(obj, models.Model):
            # Retourner un dictionnaire avec les champs du modèle
            data = {}
            for field in obj._meta.fields:
                value = getattr(obj, field.name)
                # Appel récursif pour gérer les relations
                if isinstance(value, models.Model):
                    data[field.name] = self.default(value)
                # Gérer les champs ManyToMany
                elif field.many_to_many:
                    data[field.name] = [self.default(item) for item in value.all()]
                else:
                    data[field.name] = value
            return data
        return super().default(obj)

def dumps(obj, **kwargs):
    """Fonction utilitaire pour sérialiser des objets en JSON"""
    return json.dumps(obj, cls=CustomJSONEncoder, **kwargs)

