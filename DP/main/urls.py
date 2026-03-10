from django.urls import path
from .views import *

urlpatterns = [
    path('', login_view, name='home_login'),
    path('login', login_view, name='login'),
    path('home', message, name='home'),
]
