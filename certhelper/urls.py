from django.conf.urls import url

from . import views

app_name = 'certhelper'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^list/$', views.ListView.as_view(), name='list'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    
    url(r'^create/$', views.CreateRun.as_view(), name='create'),
    url(r'^(?P<pk>[0-9]+)/update/$', views.UpdateRun.as_view(), name='update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.DeleteRun.as_view(), name='delete'),
]
