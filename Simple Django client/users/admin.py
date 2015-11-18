from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
 
from models import OrgaUser
 
class OrgaUserAdmin(UserAdmin):
    model = OrgaUser
#     fieldsets = UserAdmin.fieldsets + (
#             (None, {'fields': ('organizations',)}),
#     )
  
admin.site.register(OrgaUser, OrgaUserAdmin)
