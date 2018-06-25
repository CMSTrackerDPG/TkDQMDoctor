from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
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


class RunInfoAdmin(admin.ModelAdmin):
    exclude = ['created_at', 'updated_at', 'deleted_at']


class TypeAdmin(admin.ModelAdmin):
    exclude = ['created_at', 'updated_at', 'deleted_at']


class CategoryAdmin(admin.ModelAdmin):
    exclude = ['created_at', 'updated_at', 'deleted_at']


class SubCategoryAdmin(admin.ModelAdmin):
    exclude = ['created_at', 'updated_at', 'deleted_at']


class SubSubCategoryAdmin(admin.ModelAdmin):
    exclude = ['created_at', 'updated_at', 'deleted_at']


# Register your models here.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(ReferenceRun, ReferenceRunAdmin)
admin.site.register(RunInfo, RunInfoAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(SubSubCategory, SubSubCategoryAdmin)
