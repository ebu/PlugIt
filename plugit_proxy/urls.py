# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.conf import settings


API_BASE_PATTERN = r'ebuio_api/' if settings.PIAPI_STANDALONE else r'(?P<key>[0-9a-zA-Z]*)/(?P<hproPk>-?[0-9]*)/'


urlpatterns = patterns('plugIt.views',

    # Default PlugIt Patterns
    url(r'^' + API_BASE_PATTERN + r'$', 'api_home'),
    url(r'^' + API_BASE_PATTERN + r'user/(?P<userPk>-?[0-9]*)$', 'api_user'),
    url(r'^' + API_BASE_PATTERN + r'user/(?P<userUuid>[0-9a-z\-]*)$', 'api_user_uuid'),
    url(r'^' + API_BASE_PATTERN + r'subscriptions/(?P<userPk>-?[0-9]*)$', 'api_subscriptions'),
    url(r'^' + API_BASE_PATTERN + 'orga/(?P<orgaPk>-?[0-9]*)$', 'api_orga'),
    url(r'^' + API_BASE_PATTERN + r'members/$', 'api_get_project_members'),

    url(r'^' + API_BASE_PATTERN + r'mail/$', 'api_send_mail'),

    url(r'^' + API_BASE_PATTERN + r'orgas/$', 'api_orgas'),
    url(r'^' + API_BASE_PATTERN + r'ebuio/forum/$', 'api_ebuio_forum'),
    url(r'^' + API_BASE_PATTERN + r'ebuio/forum/search/bytag/(?P<tag>[0-9a-zA-Z]*)$', 'api_ebuio_forum_get_topics_by_tag_for_user'),

)

if settings.PIAPI_STANDALONE:
    # Standalone mode endpoints

    urlpatterns += patterns('plugIt.views',

        # Medias
        url(r'^media/(?P<path>.*)$', 'media'),

        # EBU.io Specific Patterns
        url(r'^ebuio_setUser$', 'setUser'),
        url(r'^ebuio_setOrga$', 'setOrga'),

        # Default endpoint
        url(r'^(?P<query>.*)$', 'main'),
    )


else:
    # If not add main for the project and home
    urlpatterns += patterns('plugIt.views',

        # Medias
        url(r'^(?P<hproPk>[0-9a-zA-Z_\-]*)/media/(?P<path>.*)$', 'media'),

        # Orga change
        url(r'^(?P<hproPk>[0-9a-zA-Z_\-]*)/_ebuio_setOrga$', 'setOrga'),

        # Main Pattern
        url(r'^(?P<hproPk>[0-9a-zA-Z_\-]*)/(?P<query>.*)$', 'main'),

        # Home Patterns
        url(r'^(?P<hproPk>[0-9a-zA-Z_\-]*)$', 'home'),
        url(r'^(?P<key>[0-9a-zA-Z]*)$', 'home'),
    )

