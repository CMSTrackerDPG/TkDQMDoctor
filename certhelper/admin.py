from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from nested_admin.nested import NestedStackedInline, NestedModelAdmin

from .models import *


class UserProfileInline(admin.StackedInline):
    """
    Should never be filled out manually, will be automatically created and
    filled by CERN e-groups the user is member off
    """
    model = UserProfile
    readonly_fields = ('extra_data', 'user_privilege',)
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


class ReferenceRunAdmin(admin.ModelAdmin):
    exclude = ['created_at', 'updated_at', 'deleted_at']
    list_display = (
        'reference_run', 'reco', 'runtype', 'bfield', 'beamtype', 'beamenergy',
        'dataset')


class RunInfoAdmin(admin.ModelAdmin):
    fieldsets = [
        ("User", {'fields': ['userid']}),
        ("Information", {'fields': ['type', 'reference_run', 'run_number', 'trackermap',
                                    'number_of_ls', 'int_luminosity']}),
        ("Health", {'fields': ['pixel', 'sistrip', 'tracking']}),
        ("Problem Categories", {
            'fields': ['problem_categories', 'category', 'subcategory',
                       'subsubcategory']}),
        ("Comments", {'fields': ['comment']}),
        ('Date', {'fields': ['date', 'created_at', 'updated_at']}),
    ]
    list_display = ('runtype', 'reco', 'run_number', 'is_good', 'date')
    exclude = ['deleted_at']
    readonly_fields = (
        'created_at', 'updated_at', 'category', 'subcategory', 'subsubcategory')


class TypeAdmin(admin.ModelAdmin):
    exclude = ['created_at', 'updated_at', 'deleted_at']
    list_display = ('reco', 'runtype', 'bfield', 'beamtype', 'beamenergy', 'dataset')


class ChecklistItemInline(NestedStackedInline):
    model = ChecklistItem
    extra = 3


class ChecklistItemGroupInline(NestedStackedInline):
    model = ChecklistItemGroup
    extra = 1
    inlines = [ChecklistItemInline]


class ChecklistAdmin(NestedModelAdmin):
    inlines = [ChecklistItemGroupInline]


# Register your models here.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(ReferenceRun, ReferenceRunAdmin)
admin.site.register(RunInfo, RunInfoAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(Checklist, ChecklistAdmin)
