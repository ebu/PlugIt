# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('plugIt.views',
    url(r'^media/(?P<path>.*)$', 'media'),
    url(r'^ebuio_setUser$', 'setUser'),
    url(r'^(?P<query>.*)$', 'main'),
)
