from django.conf.urls import *


urlpatterns = patterns('plugIt.views',
    url(r'^media/(?P<path>.*)$', 'media'),
    url(r'^ebuio_setUser$', 'setUser'),
    url(r'^(?P<query>.*)$', 'main'),
)
