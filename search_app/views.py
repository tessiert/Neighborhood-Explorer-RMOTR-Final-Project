from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, JsonResponse

# Create your views here.
class SearchView(View):
    def post(self, request):
        return HttpResponse(status=200)
