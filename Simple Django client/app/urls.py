from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic import RedirectView

urlpatterns = patterns('',

    (r'^$', RedirectView.as_view(url='/plugIt/')),
    url(r'^plugIt/', include('plugIt.urls')),

    (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),  # Never use this in prod !
)
