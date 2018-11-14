from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from pytz import timezone
import requests
from config.settings.base import MAP_KEY, WEATHER_KEY

from api.models import Searches

days = [{}, {}, {}]     # Data structure for 3-day weather forecast

# Create your views here.
class SearchView(View):

    # Class variables used to track state for current location
    # point_of_interest = ''  
    # radius = ''
    # sort_method = ''       

    
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


    def __init__(self):
        # variables used to track state for current location
        self.point_of_interest = ''
        self.radius = ''
        self.sort_method = ''


    # Forwarding GET to POST with included 'address' enables 'Top Searches' to 
    # function as links
    def get(self, request, address):
        return self.post(request, address)


    def post(self, request, address=''):
        global days

        DAY_FORMAT = '%A,'
        DATE_FORMAT = '%b. %d'
        # Select appropriate map zoom level based on search radius (in meters)
        map_zoom = {
            '3219': '11',
            '8047': '10',
            '16093': '9',
            '40234': '8'
        }

        # If user is doing a POI search, we've already pulled the geolocation
        # data.
        if request.POST.get('poi_search'):
            address = request.POST.get('address')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            display_order = request.POST.get('display_order')
            self.point_of_interest = request.POST.get('point_of_interest')
            self.radius = request.POST.get('radius')
            self.sort_method = request.POST.get('sort_method')
            # If declutter is checked, it will return a value, otherwise no
            # return value.  Input to mapper must be a 'boolean' text string.
            if request.POST.get('declutter'):
                declutter = 'true'
            else:
                declutter = 'false'

            places_URL = 'https://www.mapquestapi.com/search/v4/place?key={map_key}&circle={lon},{lat},{rad}&q={search_term}&sort={sort_method}'.format(
                map_key=MAP_KEY,
                lat=latitude,
                lon=longitude,
                rad=self.radius,
                search_term=self.point_of_interest,
                sort_method=self.sort_method
            )

            try:
                places_response = requests.get(places_URL).json()
            except requests.ConnectionError:
                return render(
                    request, 
                    template_name='500.html', 
                    context={'server': 'Mapquest points of interest'}, 
                    status=500
                    )

            poi_descriptions = ''
            # Initialize with marker for home location
            place_markers = 'locations={lat},{lon}|via-sm-green||'.format(
                lat=latitude,
                lon=longitude
            )
            count = 1
            for place in places_response['results']:
                poi_descriptions += str(count) + '. ' \
                    + place['displayString'] + '\n\n'
                place_markers += str(place['place']['geometry']['coordinates'][1]) \
                    + ',' + str(place['place']['geometry']['coordinates'][0]) + '|' \
                    + 'marker-sm-red-' + str(count) + '||'
                count += 1
            place_markers = place_markers.rstrip('|')                

            map_URL = 'https://www.mapquestapi.com/staticmap/v5/map?key={map_key}&center={lat},{lon}&size=260,200@2x&scalebar=true&&zoom={zoom}&declutter={declutter}&{places}'.format(
                map_key=MAP_KEY,
                lat=latitude,
                lon=longitude,
                zoom=map_zoom[self.radius],
                declutter=declutter,
                places=place_markers
            )

            if not poi_descriptions:
                poi_descriptions = 'No locations found.'
        
            context = {
                'formatted_address': address,
                'latitude': latitude,
                'longitude': longitude,
                'temperature': request.POST.get('temperature'), 
                'summary': request.POST.get('summary'),
                'days': days,
                'map_url': map_URL,
                'poi_descriptions': poi_descriptions,
                'poi_start_val': self.point_of_interest,
                'radius_start_val': self.radius,
                'sort_start_val': self.sort_method,
                'anchor': 'poi_anchor'
                }
            return render(request, template_name='pages/search.html', context=context)

        # If address is supplied, then user clicked a 'Top Searches' link.
        # If not, get address from posted search bar form data.
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

        for i in range(3):
            cur_data = weather_response['daily']['data'][i]
            cur_day = today + timedelta(days=i) # today, tomorrow, day after

            # Store 3-day forecast info in class variable, so we don't have
            # to retreive it again if a POI search is performed
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
            'latitude': latitude,
            'longitude': longitude,
            'temperature': round(weather_response['currently']['temperature']), 
            'summary': weather_response['currently']['summary'],
            'days': days,
            'map_url': map_URL,
            'poi_descriptions': 'Top ten matches will appear here.',
            'poi_start_val': self.point_of_interest,
            'radius_start_val': self.radius,
            'sort_start_val': self.sort_method
            }
        return render(request, template_name='pages/search.html', context=context)