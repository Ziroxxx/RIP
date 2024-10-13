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
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/planets', views.planetMethods.as_view(), name='getPlanets'),
    path('api/planet/<int:pk>', views.one_planet.as_view(), name='getPlanet'),
    path('api/planet/<int:pk>/add_image', views.add_image, name='setImg'),

    path('api/cons_periods', views.cons_periods.as_view(), name='getRequests'),
    path('api/cons_period/<int:pk>', views.one_cons_period.as_view(), name='getRequest'),
    path('api/cons_period/<int:pk>/save-by-creator', views.save_by_creator, name='saveByCreator'),
    path('api/cons_period/<int:pk>/moderate', views.moderateByCreator.as_view(), name='moderateRequest'),

    path('api/mm/<int:pk_req>/<int:pk_planet>', views.MMMethods.as_view(), name='deleteFromReq'),
    path('api/user/reg', views.userReg.as_view(), name='register'),
    path('api/user/<int:pk>', views.userProfile.as_view(), name='putUser'),
    path('api/user/login', views.userLogin.as_view(), name='authUser'),
    path('api/user/logout', views.userLogout.as_view(), name='logoutUser'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')
]
