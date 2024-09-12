"""
URL configuration for astro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from astro import views 
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.getServices, name = 'home'),
    path('planet/<int:planet_id>/', views.getPlanet, name = 'PlanetID'),
    path('wish/<int:wish_id>', views.getWishList, name = 'wish'),
    path('add', views.addPlanet, name = 'addPlanet'),
    path('delWish', views.removeDraft, name = 'delWish'),
]
