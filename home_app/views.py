from django.shortcuts import render
from django.views.generic import View

from api.models import Searches

# Create your views here.
class HomeView(View):

    NUM_TOP_SEARCHES = 5

    def get(self, request):
        top_searches = Searches.objects.order_by('-count')[:self.NUM_TOP_SEARCHES]
        return render(
            request, 
            template_name='pages/home.html', 
            context={'top_searches': top_searches}
            )