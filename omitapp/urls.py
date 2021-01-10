from django.urls import path

app_name = 'omitapp'

from .views import *

urlpatterns=[
    path('main/', main_view, name='main'),
    path('create/', temp_view, name='create')
]