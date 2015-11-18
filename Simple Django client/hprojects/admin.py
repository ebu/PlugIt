from django.contrib import admin

from models import HostedProject

class HostedProjectAdmin(admin.ModelAdmin):
    list_display = ('name','plugItURI',)
admin.site.register(HostedProject, HostedProjectAdmin)
