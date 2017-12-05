from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'certhelper'
urlpatterns = [
    url(r'^$', views.listruns, name='list'),
    url(r'^clearsession/$', login_required(views.clearsession),           name='clearsession'),
    url(r'^summary/$',                   views.SummaryView.as_view(),     name='summary'),
    url(r'^references/$',                views.ListReferences.as_view(),  name='references'),
    url(r'^create/$',       login_required(views.CreateRun.as_view()),    name='create'),
    url(r'^createtype/$',   login_required(views.CreateType.as_view()),   name='createtype'),

    url(r'^(?P<pk>[0-9]+)/update/$', login_required(views.UpdateRun.as_view()), name='update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', login_required(views.DeleteRun.as_view()), name='delete'),

    # checklists
    url(r'^checklists/trackermap$', TemplateView.as_view(template_name='certhelper/checklists/trackermap.html'), name='trackermap_checklist'),
    url(r'^checklists/pixel$',      TemplateView.as_view(template_name='certhelper/checklists/pixel.html'),      name='pixel_checklist'),
    url(r'^checklists/sistrip$',    TemplateView.as_view(template_name='certhelper/checklists/sistrip.html'),    name='sistrip_checklist'),
    url(r'^checklists/tracking$',   TemplateView.as_view(template_name='certhelper/checklists/tracking.html'),   name='tracking_checklist'),

    # info
    url(r'^help/$',       TemplateView.as_view(template_name='certhelper/info/help.html'),    name='help'),
    url(r'^info/comment', TemplateView.as_view(template_name='certhelper/info/comment.html'), name='comment_info'),

    # authentification
    url(r'^accounts/login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^accounts/logout/$', views.logout_view, name='logout'),
]
