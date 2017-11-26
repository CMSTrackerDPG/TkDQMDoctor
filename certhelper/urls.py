from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

app_name = 'certhelper'
urlpatterns = [
    url(r'^$', views.listruns, name='list'),
    url(r'^clearsession/$', views.clearsession, name='clearsession'),
    url(r'^summary/$', views.SummaryView.as_view(), name='summary'),
    url(r'^references/$', views.ListBlocks.as_view(), name='references'),
    url(r'^create/$', views.CreateRun.as_view(), name='create'),
    url(r'^createtype/$', views.CreateType.as_view(), name='createtype'),

    url(r'^(?P<pk>[0-9]+)/update/$', views.UpdateRun.as_view(), name='update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.DeleteRun.as_view(), name='delete'),

    # checklists
    url(r'^checklists/trackermap$', TemplateView.as_view(template_name='certhelper/checklists/trackermap.html'), name='trackermap_checklist'),
    url(r'^checklists/pixel$', TemplateView.as_view(template_name='certhelper/checklists/pixel.html'), name='pixel_checklist'),
    url(r'^checklists/sistrip$', TemplateView.as_view(template_name='certhelper/checklists/sistrip.html'), name='sistrip_checklist'),
    url(r'^checklists/tracking$', TemplateView.as_view(template_name='certhelper/checklists/tracking.html'), name='tracking_checklist'),
]
