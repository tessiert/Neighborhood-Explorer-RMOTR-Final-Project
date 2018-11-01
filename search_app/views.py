from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, JsonResponse

import requests

# Create your views here.
class SearchView(View):
    def post(self, request):
        address = request.POST.get('address', '')
        encoded_address = address.replace(' ', '%20')
        geocode_URL = 'http://www.mapquestapi.com/geocoding/v1/address?key=X49B68O9Ab2W453JbXi1S8jC9AswBGP7&location={}'.format(encoded_address)
        geo_response = requests.get(geocode_URL).json()
        # Get latitude and longitude for remaining API lookups
        latitude = geo_response['results'][0]['locations'][0]['latLng']['lat']
        longitude = geo_response['results'][0]['locations'][0]['latLng']['lng']
        # Get weather at given geolocation
        weather_URL = 'https://api.darksky.net/forecast/b7e6ab1963787cc564ae9055b3b4b313/{},{}'.format(latitude, longitude)     
        weather_response = requests.get(weather_URL).json()
        return JsonResponse(weather_response, status=200)
