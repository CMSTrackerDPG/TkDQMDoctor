from django.conf.urls import url

from . import views

app_name = 'certhelper'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^list/$', views.list, name='list'),
    url(r'^helper/$', views.helper, name='helper'),
    url(r'^(?P<runinfo_id>[0-9]+)/$', views.detail, name='detail'),
]
