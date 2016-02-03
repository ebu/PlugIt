# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.conf import settings

urlpatterns = patterns('plugIt.views',)

if settings.PIAPI_STANDALONE:
    # If in standalone mode add the default routes for media and EBU.io user mgmt
    urlpatterns += patterns('plugIt.views',
        # Media patterns
        url(r'^media/(?P<path>.*)$', 'media'),

        # EBU.io Specific Patterns
        url(r'^ebuio_logout$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
        url(r'^ebuio_login$', 'django.contrib.auth.views.login'),
        url(r'^ebuio_setUser$', 'setUser'),
        url(r'^ebuio_setOrga$', 'setOrga'),
   )

urlpatterns += patterns('plugIt.views',

    # Default PlugIt Patterns
    url(r'^(?P<key>[0-9a-zA-Z]*)/(?P<hproPk>-?[0-9]*)/$', 'api_home'),
    url(r'^(?P<key>[0-9a-zA-Z]*)/(?P<hproPk>-?[0-9]*)/user/(?P<userPk>-?[0-9]*)$', 'api_user'),
    url(r'^(?P<key>[0-9a-zA-Z]*)/(?P<hproPk>-?[0-9]*)/user/(?P<userUuid>[0-9a-z\-]*)$', 'api_user_uuid'),
    url(r'^(?P<key>[0-9a-zA-Z]*)/(?P<hproPk>-?[0-9]*)/subscriptions/(?P<userPk>-?[0-9]*)$', 'api_subscriptions'),
    url(r'^(?P<key>[0-9a-zA-Z]*)/(?P<hproPk>-?[0-9]*)/orga/(?P<orgaPk>-?[0-9]*)$', 'api_orga'),
    url(r'^(?P<key>[0-9a-zA-Z]*)/(?P<hproPk>-?[0-9]*)/members/$', 'api_get_project_members'),

    url(r'^(?P<key>[0-9a-zA-Z]*)/(?P<hproPk>-?[0-9]*)/mail/$', 'api_send_mail'),

    url(r'^(?P<key>[0-9a-zA-Z]*)/(?P<hproPk>-?[0-9]*)/orgas/$', 'api_orgas'),
    url(r'^(?P<key>[0-9a-zA-Z]*)/(?P<hproPk>-?[0-9]*)/ebuio/forum/$', 'api_ebuio_forum'),
    url(r'^(?P<key>[0-9a-zA-Z]*)/(?P<hproPk>-?[0-9]*)/ebuio/forum/search/bytag/(?P<tag>[0-9a-zA-Z]*)$', 'api_ebuio_forum_get_topics_by_tag_for_user'),

    url(r'^(?P<hproPk>[0-9a-zA-Z_\-]*)/media/(?P<path>.*)$', 'media'),
    url(r'^(?P<hproPk>[0-9a-zA-Z_\-]*)/_ebuio_setOrga$', 'setOrga'),

)

if settings.PIAPI_STANDALONE:
    # If in standalone mode add the final main rule
    urlpatterns += patterns('plugIt.views',
        # Final Route for Standalone
        url(r'^(?P<query>.*)$', 'main'),
    )
else:
    # If not add main for the project and home
    urlpatterns += patterns('plugIt.views',

        # Main Pattern
        url(r'^(?P<hproPk>[0-9a-zA-Z_\-]*)/(?P<query>.*)$', 'main'),

        # Home Patterns
        url(r'^(?P<hproPk>[0-9a-zA-Z_\-]*)$', 'home'),
        url(r'^(?P<key>[0-9a-zA-Z]*)$', 'home'),
    )