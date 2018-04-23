"""
This file sets links the url that is accessed to the corresponding view which
renders a page. The closely related views are found in ./views.py

These pages can have a namespace (certhelper), and a name such that it is possible to link to them
with their name, instead of hardcoded paths.
This allows for a decoupling of the page and url.

Furthermore the login_required(VIEW) function takes care of authentification.
If a page does not require a login to be viewed one can still check if the current user is logged in
with    "{% if not user.is_authenticated %}" as it is used in list.html to display buttons depending on
the access privileges.
"""

from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'certhelper'
urlpatterns = [
    url(r'^$', views.listruns, name='list'),
    url(r'^clearsession/$', login_required(views.clearsession),            name='clearsession'),
    url(r'^summary/$',      login_required(views.summaryView),   name='summary'),
    url(r'^references/$',                  views.ListReferences.as_view(), name='references'),
    url(r'^create/$',       login_required(views.CreateRun.as_view()),     name='create'),
    url(r'^createtype/$',   login_required(views.CreateType.as_view()),    name='createtype'),

    url(r'^(?P<pk>[0-9]+)/update/$', login_required(views.UpdateRun.as_view()), name='update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', login_required(views.DeleteRun.as_view()), name='delete'),

    # checklists
    url(r'^checklists/general$',    TemplateView.as_view(template_name='certhelper/checklists/general.html'),    name='general_checklist'),
    url(r'^checklists/trackermap$', TemplateView.as_view(template_name='certhelper/checklists/trackermap.html'), name='trackermap_checklist'),
    url(r'^checklists/pixel$',      TemplateView.as_view(template_name='certhelper/checklists/pixel.html'),      name='pixel_checklist'),
    url(r'^checklists/sistrip$',    TemplateView.as_view(template_name='certhelper/checklists/sistrip.html'),    name='sistrip_checklist'),
    url(r'^checklists/tracking$',   TemplateView.as_view(template_name='certhelper/checklists/tracking.html'),   name='tracking_checklist'),

    # info
    url(r'^help/$',       TemplateView.as_view(template_name='certhelper/info/help.html'),    name='help'),
    url(r'^info/comment', TemplateView.as_view(template_name='certhelper/info/comment.html'), name='comment_info'),

    # authentification
    url(r'^accounts/login/$', auth_views.LoginView.as_view(), name='login'), # in settings.py the redirect after logging in is defined
                                                                             # currently that is "/" which corresponds to views.listruns
    url(r'^accounts/logout/$', views.logout_view, name='logout'),
    url('ajax/load-subcategories/', views.load_subcategories, name='ajax_load_subcategories'),
    url('ajax/load-subsubcategories/', views.load_subsubcategories, name='ajax_load_subsubcategories'),
]
