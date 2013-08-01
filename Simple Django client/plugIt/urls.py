# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
	'plugIt.views',
    url(r'^media/(?P<path>.*)$', 'media'),
    url(r'^ebuio_setUser$', 'setUser'),
    url(r'^ebuio_setOrga$', 'setOrga'),
    
    
    url(r'^ebuio_api/$', 'api_home'),
    url(r'^ebuio_api/user/(?P<userPk>[\-0-9]*)$', 'api_user'),

    url(r'^(?P<query>.*)$', 'main'),
)
