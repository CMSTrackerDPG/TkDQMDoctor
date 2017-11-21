from django.conf.urls import url

from . import views

app_name = 'certhelper'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^helper/$', views.helper, name='helper'),
    url(r'^list/$', views.ListView.as_view(), name='list'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
]
