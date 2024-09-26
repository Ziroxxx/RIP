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

from astro_app import views 
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.getServices, name = 'home'),
    path('planet/<int:planet_id>/', views.getPlanet, name = 'PlanetID'),
    path('wish/<int:wish_id>', views.getWishList, name = 'wish'),
    path('add', views.addPlanet, name = 'addPlanet'),
    path('delWish', views.removeDraft, name = 'delWish'),

    path('api/planets/', views.planetMethods.as_view(), name='getPlanets'),
    path('api/planet/<int:pk>', views.one_planet.as_view(), name='getPlanet'),
    path('api/planet/<int:pk>/post', views.add_image, name='setImg'),

    path('api/requests', views.requests.as_view(), name='getRequests'),
    path('api/request/<int:pk>', views.one_request.as_view(), name='getRequest'),
    path('api/request/<int:pk>/save-by-creator', views.save_by_creator, name='saveByCreator'),
    path('api/request/<int:pk>/moderate', views.moderate, name='moderateRequest'),

    path('api/mm/<int:pk_req>/<int:pk_planet>', views.MMMethods.as_view(), name='deleteFromReq'),
    path('api/user/register', views.userMethods.as_view(), name='register'),
    path('api/user/<int:pk>', views.userMethods.as_view(), name='putUser'),
    path('api/user/<int:pk>/auth', views.autentification, name='authUser'),
    path('api/user/<int:pk>/logout', views.logout, name='logoutUser')
]
