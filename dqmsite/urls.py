from django.conf.urls import include, url
from django.contrib import admin
from allauth.account import views as allauth_views
from importlib import import_module

urlpatterns = [
    url(r'^', include('certhelper.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^nested_admin/', include('nested_admin.urls')),
]