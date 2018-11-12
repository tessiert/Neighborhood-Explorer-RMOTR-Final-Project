from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from pytz import timezone
import requests
from config.settings.base import MAP_KEY, WEATHER_KEY

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
        DAY_FORMAT = '%A,'
        DATE_FORMAT = '%b. %d'

        if not address:
            address = request.POST.get('address', '')
        encoded_address = address.replace(' ', '%20')
        geocode_URL = 'http://www.mapquestapi.com/geocoding/v1/address?key={}&location={}'.format(
            MAP_KEY,
            encoded_address
            )
        try:
            geo_response = requests.get(geocode_URL).json()
        except requests.ConnectionError:
            return render(
                request, 
                template_name='500.html', 
                context={'server': 'Mapquest geolocation'}, 
                status=500
                )

        location_data = geo_response['results'][0]['locations'][0]
        if (
            geo_response['info']['statuscode'] != 0 
            or location_data['adminArea3'] == ''
            or location_data['adminArea1'] != 'US'
        ):
            return render(request, template_name='404.html', status=404)

        # Pull address data from response
        street = location_data['street']
        city = location_data['adminArea5']
        state = location_data['adminArea3']
        zip_code = location_data['postalCode']

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
        latitude = location_data['latLng']['lat']
        longitude = location_data['latLng']['lng']
        # Get weather at given geolocation
        weather_URL = 'https://api.darksky.net/forecast/{}/{},{}'.format(
            WEATHER_KEY,
            latitude, 
            longitude
            )     
        try:
            weather_response = requests.get(weather_URL).json()
        except requests.ConnectionError:
            return render(request, template_name='500.html', context={'server': 'Dark Sky weather'}, status=500)

        # Get current date in time zone of address
        zone = weather_response['timezone']
        today = datetime.now(timezone(zone))

        days = [{}, {}, {}]
        for i in range(3):
            cur_data = weather_response['daily']['data'][i]
            cur_day = today + timedelta(days=i) # today, tomorrow, day after

            days[i]['name'] = cur_day.strftime(DAY_FORMAT)
            days[i]['date'] = cur_day.strftime(DATE_FORMAT)
            days[i]['low'] = round(cur_data['temperatureLow'])
            days[i]['high'] = round(cur_data['temperatureHigh'])
            days[i]['image'] = self._get_weather_image(cur_data['icon'])
            days[i]['text'] = cur_data['icon']

        # places_URL = 'https://www.mapquestapi.com/search/v4/place?key={}&location={},{}&sort=distance

        map_URL = 'https://www.mapquestapi.com/staticmap/v5/map?key={}&center={},{}&size=260,200@2x&scalebar=true&zoom=14&locations={},{}|via-sm-green&declutter=true'.format(
            MAP_KEY,
            latitude,
            longitude,
            latitude,
            longitude
        )
       
        context = {
            'formatted_address': formatted_address.title(),
            'temperature': round(weather_response['currently']['temperature']), 
            'summary': weather_response['currently']['summary'],
            'days': days,
            'map_url': map_URL
            }
        return render(request, template_name='pages/search.html', context=context)
        #return JsonResponse(geo_response)