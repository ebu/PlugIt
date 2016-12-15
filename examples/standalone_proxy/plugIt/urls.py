# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',

    url(r'^ebuio_logout$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^ebuio_login$', 'django.contrib.auth.views.login'),

)

urlpatterns += patterns(
    'plugIt.views',

    # Regular patterns
    url(r'^media/(?P<path>.*)$', 'media'),
    url(r'^ebuio_setUser$', 'setUser'),
    url(r'^ebuio_setOrga$', 'setOrga'),

    # API Endpoints with /ebuio_api/
    url(r'^ebuio_api/$', 'api_home'),
    url(r'^ebuio_api/user/(?P<userPk>-?[0-9]*)$', 'api_user'),
    url(r'^ebuio_api/user/(?P<userUuid>[0-9a-z\-]*)$', 'api_user_uuid'),
    url(r'^ebuio_api/subscriptions/(?P<userPk>-?[0-9]*)$', 'api_subscriptions'),
    url(r'^ebuio_api/orga/(?P<orgaPk>-?[0-9]*)$', 'api_orga'),
    url(r'^ebuio_api/members/$', 'api_get_project_members'),
    url(r'^ebuio_api/mail/$', 'api_send_mail'),
    url(r'^ebuio_api/orgas/$', 'api_orgas'),
    url(r'^ebuio_api/ebuio/forum/$', 'api_ebuio_forum'),
    url(r'^ebuio_api/ebuio/forum/search/bytag/(?P<tag>[0-9a-zA-Z]*)$', 'api_ebuio_forum_get_topics_by_tag_for_user'),

    # url(r'^(?P<hproPk>[0-9a-zA-Z_\-]*)/media/(?P<path>.*)$', 'media'),
    # url(r'^(?P<hproPk>[0-9a-zA-Z_\-]*)/_ebuio_setOrga$', 'setOrga'),

    # url(r'^(?P<hproPk>[0-9a-zA-Z_\-]*)/(?P<query>.*)$', 'main'),
    # url(r'^(?P<hproPk>[0-9a-zA-Z_\-]*)$', 'home'),
    # url(r'^(?P<key>[0-9a-zA-Z]*)$', 'home'),

    # Final Route
    url(r'^(?P<query>.*)$', 'main'),

)
