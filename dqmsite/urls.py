from django.conf.urls import include, url
from django.contrib import admin
from allauth.account import views as allauth_views
from importlib import import_module

urlpatterns = [
    url(r'^', include('certhelper.urls')),
    url(r'^admin/', admin.site.urls),
    url(r"^login/$", allauth_views.login, name="account_login"),
    url(r"^logout/$", allauth_views.logout, name="account_logout"),
    url(r"^signup/$", allauth_views.signup, name="account_signup"),
]

urlpatterns += getattr(import_module('cern_oauth2.urls'), 'urlpatterns', None)