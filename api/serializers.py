from rest_framework import serializers

from api.models import Searches

class SearchesModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Searches
        fields = ('city', 'state', 'count')
