from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response

from api.models import Searches
from api.serializers import SearchesModelSerializer

# Create your views here.

# Right now, I'm only allowing an external api 'GET' of a list view,
# and so using ViewSet rather than the more powerful ModelViewSet 
class SearchesViewSet(viewsets.ViewSet):

    def list(self, request):
        qs = Searches.objects.all()
        serializer = SearchesModelSerializer(qs, many=True)
        return Response(serializer.data)