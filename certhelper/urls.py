from django.conf.urls import url

from . import views

app_name = 'certhelper'
urlpatterns = [
    # url(r'^$', views.index, name='index'),
    url(r'^$', views.listruns, name='list'),
    url(r'^clearsession/$', views.clearsession, name='clearsession'),
    url(r'^summary/$', views.SummaryView.as_view(), name='summary'),
    url(r'^references/$', views.ListBlocks.as_view(), name='references'),
    url(r'^create/$', views.CreateRun.as_view(), name='create'),
    url(r'^createtype/$', views.CreateType.as_view(), name='createtype'),

    url(r'^(?P<pk>[0-9]+)/update/$', views.UpdateRun.as_view(), name='update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.DeleteRun.as_view(), name='delete'),
]
