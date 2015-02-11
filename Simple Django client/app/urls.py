# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic import RedirectView

from django.utils.translation import ugettext_lazy as _

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

if settings.PIAPI_STANDALONE:
	urlpatterns = patterns('',
	
		url(r'^admin/', include(admin.site.urls)),
	
	   	(r'^$', RedirectView.as_view(url='/plugIt/')),
		url(r'^plugIt/', include('plugIt.urls')),
	
	
	    (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),  # Never use this in prod !
	)
else:
	urlpatterns = patterns('',
	
		url(r'^admin/', include(admin.site.urls)),
	
	   	(r'^$', RedirectView.as_view(url='/plugIt/1/')),
		url(r'^plugIt/', include('plugIt.urls')),
	
	
	    (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),  # Never use this in prod !
	)

# for Django >= 1.7
admin.site.site_header = _('PlugIt administration') # "Django administration"
admin.site.site_title = _('PlugIt site admin') # "Django site admin"
admin.site.index_title = _('Site administration') # "Site administration"
