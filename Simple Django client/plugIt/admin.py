from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from models import Organization, OrgaUser


# Define a new User admin
class OrgaUserAdmin(UserAdmin):
    model = OrgaUser
    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('organization',)}),
    )
admin.site.register(OrgaUser, OrgaUserAdmin)

admin.site.register(Organization)