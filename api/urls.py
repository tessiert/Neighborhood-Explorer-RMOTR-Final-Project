from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from api import views


router = DefaultRouter()

router.register('api', views.SearchesViewSet, base_name='api')

urlpatterns = [
]

urlpatterns += router.urls