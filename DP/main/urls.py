from django.urls import path
from .views import *

urlpatterns = [
    path('', login_view, name='home_login'),
    path('login', login_view, name='login'),
    path('home', message, name='home'),
    path('logout', logout_view, name='logout'),
    path('link', token_link, name='link'),
    path('secret/<uuid:token>/', read_secret, name='read_secret'),
]
