from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from pytz import timezone
import requests

from api.models import Searches

# Create your views here.
class SearchView(View):

    @classmethod
    def _get_weather_image(cls, icon):
        path = '/static/images/weather/'
        if icon in ['cloudy', 'fog']:
            return path + 'cloudy.png'
        if icon in ['partly-cloudy-day', 'partly-cloudy-night']:
            return path + 'partly-cloudy-day.png'
        if icon in ['clear-day', 'clear-night']:
            return path + 'clear-day.png'
        if icon in ['snow', 'sleet']:
            return path + 'winter.png'
        else:
            return path + icon + '.png'


    # Enables 'Top Searches' to function as links
    def get(self, request, address):
        return self.post(request, address)


    def post(self, request, address=''):
        if not address:
            address = request.POST.get('address', '')
        encoded_address = address.replace(' ', '%20')
        geocode_URL = 'http://www.mapquestapi.com/geocoding/v1/address?key=X49B68O9Ab2W453JbXi1S8jC9AswBGP7&location={}'.format(encoded_address)
        try:
            geo_response = requests.get(geocode_URL).json()
        except requests.ConnectionError:
            return render(request, template_name='500.html', context={'server': 'Mapquest geolocation'}, status=500)
        if (
            geo_response['info']['statuscode'] != 0 
            or geo_response['results'][0]['locations'][0]['adminArea3'] == ''
            or geo_response['results'][0]['locations'][0]['adminArea1'] != 'US'
        ):
            return render(request, template_name='404.html', status=404)

        # Pull address data from response
        street = geo_response['results'][0]['locations'][0]['street']
        city = geo_response['results'][0]['locations'][0]['adminArea5']
        state = geo_response['results'][0]['locations'][0]['adminArea3']
        zip_code = geo_response['results'][0]['locations'][0]['postalCode']

        # Format the address to contain as much data as possible, with no
        # hanging commas for missing pieces
        formatted_address = '{street}, {city}, {state}, {zip_code}'.format(
            street=street,
            city=city,
            state=state,
            zip_code=zip_code
        ).lstrip(' ,').rstrip(' ,')

        # If the current search is being done at least at city level accuracy,
        # update count of, or add new record to top searches database
        try:
            city_search = Searches.objects.get(city=city, state=state)
            city_search.count += 1
        except Searches.DoesNotExist:
            city_search = Searches(city=city, state=state, count=1)
        city_search.save()

        # Get latitude and longitude for remaining API lookups
        latitude = geo_response['results'][0]['locations'][0]['latLng']['lat']
        longitude = geo_response['results'][0]['locations'][0]['latLng']['lng']
        # Get weather at given geolocation
        weather_URL = 'https://api.darksky.net/forecast/b7e6ab1963787cc564ae9055b3b4b313/{},{}'.format(latitude, longitude)     
        try:
            weather_response = requests.get(weather_URL).json()
        except requests.ConnectionError:
            return render(request, template_name='500.html', context={'server': 'Dark Sky weather'}, status=500)

        today_data = weather_response['daily']['data'][0]
        tomorrow_data = weather_response['daily']['data'][1]
        day_after_data = weather_response['daily']['data'][2]

        # Get image file locations for 3-day forecast
        today_weather_image = self._get_weather_image(today_data['icon'])
        tomorrow_weather_image = self._get_weather_image(tomorrow_data['icon'])
        day_after_weather_image = self._get_weather_image(day_after_data['icon'])

        # Extract corresponding dates
        zone = weather_response['timezone']
        today = datetime.now(timezone(zone))
        tomorrow = today + timedelta(days=1)
        day_after = today + timedelta(days=2)
        day_format = '%A,'
        date_format = '%b. %d'

        context = {
            'formatted_address': formatted_address.title(),
            'temperature': round(weather_response['currently']['temperature']), 
            'summary': weather_response['currently']['summary'],
            'today_day': today.strftime(day_format),
            'today_date': today.strftime(date_format),
            'today_temp_low': round(today_data['temperatureLow']),
            'today_temp_high': round(today_data['temperatureHigh']),
            'today_weather_image': today_weather_image,
            'today_weather_text': today_data['icon'],
            'tomorrow_day': tomorrow.strftime(day_format),
            'tomorrow_date': tomorrow.strftime(date_format),
            'tomorrow_temp_low': round(tomorrow_data['temperatureLow']),
            'tomorrow_temp_high': round(tomorrow_data['temperatureHigh']),
            'tomorrow_weather_image': tomorrow_weather_image,
            'tomorrow_weather_text': tomorrow_data['icon'],
            'day_after_day': day_after.strftime(day_format),
            'day_after_date': day_after.strftime(date_format),
            'day_after_temp_low': round(day_after_data['temperatureLow']),
            'day_after_temp_high': round(day_after_data['temperatureHigh']),
            'day_after_weather_image': day_after_weather_image,
            'day_after_weather_text': day_after_data['icon']
            }
        return render(request, template_name='pages/search.html', context=context)
        #return JsonResponse(geo_response)
