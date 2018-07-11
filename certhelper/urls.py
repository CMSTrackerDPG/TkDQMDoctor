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

from certhelper.views import ChecklistTemplateView
from . import views

app_name = 'certhelper'
urlpatterns = [
    url(r'^$', views.listruns, name='list'),
    url(r'^shiftleader/$', views.shiftleader_view, name='shiftleader'),
    url(r'^summary/$', views.summaryView, name='summary'),
    url(r'^references/$', views.ListReferences.as_view(), name='references'),
    url(r'^create/$', views.CreateRun.as_view(), name='create'),
    url(r'^createtype/$', views.CreateType.as_view(), name='createtype'),

    url(r'^(?P<pk>[0-9]+)/update/$', views.UpdateRun.as_view(), name='update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.DeleteRun.as_view(), name='delete'),

    url(r'^(?P<run_number>[0-9]+)/harddelete/$', views.hard_deleteview, name='harddelete'),
    url(r'^(?P<pk>[0-9]+)/hard_delete_run/$', views.hard_delete_run_view, name='hard_delete_run'),
    url(r'^(?P<pk>[0-9]+)/restore_run/$', views.restore_run_view, name='restore_run'),

    # checklists
    url(r'^checklists/general$', ChecklistTemplateView.as_view(
        template_name='certhelper/checklists/general.html'),
        name='general_checklist'),
    url(r'^checklists/trackermap$', ChecklistTemplateView.as_view(
        template_name='certhelper/checklists/trackermap.html'),
        name='trackermap_checklist'),
    url(r'^checklists/pixel$', ChecklistTemplateView.as_view(
        template_name='certhelper/checklists/pixel.html'),
        name='pixel_checklist'),
    url(r'^checklists/sistrip$', ChecklistTemplateView.as_view(
        template_name='certhelper/checklists/sistrip.html'),
        name='sistrip_checklist'),
    url(r'^checklists/tracking$', ChecklistTemplateView.as_view(
        template_name='certhelper/checklists/tracking.html'),
        name='tracking_checklist'),

    # info
    url(r'^help/$', TemplateView.as_view(
        template_name='certhelper/info/help.html'), name='help'),
    url(r'^info/comment', TemplateView.as_view(
        template_name='certhelper/info/comment.html'), name='comment_info'),

    # logout
    url(r'^logout/', views.logout_view, name='logout'),
    url(r'^logout-status/', views.logout_status, name='logout_status'),

    url(r'^ajax/load-subcategories/$', views.load_subcategories, name='ajax_load_subcategories'),
    url(r'^ajax/load-subsubcategories/$', views.load_subsubcategories, name='ajax_load_subsubcategories'),
    url(r'^ajax/validate-cc-list/$', views.validate_central_certification_list, name='ajax_validate_cc_list'),
]
