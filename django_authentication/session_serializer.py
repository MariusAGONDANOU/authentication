import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.sessions.serializers import JSONSerializer
from .serializers import CustomJSONEncoder

class CustomSessionSerializer(JSONSerializer):
    """
    Serializer personnalisé pour les sessions Django qui utilise notre CustomJSONEncoder.
    """
    def dumps(self, obj):
        return json.dumps(
            obj, separators=(',', ':'),
            cls=CustomJSONEncoder,
        ).encode('latin-1')



