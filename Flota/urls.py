"""Flota URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from Pojazd.models import Pojazd
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from Pojazd.views import pojazd_opis_view, pojazdHistoria_find_view, pojazd_find_view, home_view, pojazd_create_view, magazyn_view, pojazd_usun_view, opona_create_view, felga_create_view
from Pojazd.views import pojazd_zmiana_opon_view,  historia_create_view, historia_przebiegu_create_view, login_view, logout_view, user_find_view, przedmiot_view, usun_przedmiot, zapisz_view, wheels_create_view, kontakt_view


urlpatterns = [
    path('admin99/', admin.site.urls),
    path('login/',  login_view, name='login' ),
    path('logout/', logout_view, name='logout'),
    path('', home_view, name='home' ),
    path('pojazd/<str:rejestracja>', pojazd_opis_view ),
    path('usun/<str:rejestracja>', pojazd_usun_view ),
    path('historia-find/',  pojazdHistoria_find_view, name='historia-find' ),
    path('find/',  pojazd_find_view, name='find'),
    path('user-find/',  user_find_view, name='user-find'),
    path('magazyn/',  magazyn_view, name='magazyn'),
    path('zapisz/', zapisz_view, name='zapisz'),
    path('nowy/',  pojazd_create_view, name='nowy'),
    path('nowe-kola', wheels_create_view, name='nowe-kola'),
    path('nowa-opona/',  opona_create_view, name='nowa-opona'),
    path('nowy-wpis/',  historia_create_view, name='nowy-wpis'),
    path('nowy-przejazd/',  historia_przebiegu_create_view, name='nowy-przejazd'),
    path('nowa-felga/',  felga_create_view, name='nowa-felga'),
    path('zmiana-opon/',  pojazd_zmiana_opon_view, name='zmiana-opon'),
    path('przedmiot/<str:id>', przedmiot_view, name="przedmiot-view" ),
    path('usun-przedmiot/<str:id>', usun_przedmiot, name="usun-przedmiot" ),
    path('kontakt', kontakt_view, name='kontakt'),
    
   

] +  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
