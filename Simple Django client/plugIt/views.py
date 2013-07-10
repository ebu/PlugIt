#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.utils.encoding import smart_str
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db import connections
from django.core.paginator import InvalidPage, EmptyPage, Paginator
from django.core.cache import cache
from django import forms

from django.db.models import Q

from plugIt import PlugIt

from django.views.decorators.cache import cache_control

from django.template import Context, Template
from django.core.context_processors import csrf

from django.core.cache import cache

from django.contrib.auth.models import User, AnonymousUser


# Standalone mode: Load the main plugit interface
if settings.PIAPI_STANDALONE:
    plugIt = PlugIt(settings.PIAPI_STANDALONE_URI)


def main(request, query):

    def gen404(reason):
        """Return a 404 error"""
        return HttpResponseNotFound(render_to_response('plugIt/404.html', {'reason': reason, 'ebuio_baseUrl':  settings.PIAPI_BASEURI, 'ebuio_userMode': request.session.get('plugit-standalone-usermode', 'ano')}, context_instance=RequestContext(request)))

    def gen403(reason):
        """Return a 403 error"""
        return HttpResponseNotFound(render_to_response('plugIt/403.html', {'reason': reason, 'ebuio_baseUrl':  settings.PIAPI_BASEURI, 'ebuio_userMode': request.session.get('plugit-standalone-usermode', 'ano')}, context_instance=RequestContext(request)))

    # Get meta
    meta = plugIt.getMeta(query)

    if not meta:
        return gen404('meta')

    ## If standalone mode, change the current user based on parameters
    if settings.PIAPI_STANDALONE:
        currentUserMode = request.session.get('plugit-standalone-usermode', 'ano')

        if currentUserMode == 'log':
            request.user = User(pk=-1, username='Logged')
            request.user.ebuio_member = False
            request.user.ebuio_admin = False
        elif currentUserMode == 'mem':
            request.user = User(pk=-2, username='Member')
            request.user.ebuio_member = True
            request.user.ebuio_admin = False
        elif currentUserMode == 'adm':
            request.user = User(pk=-3, username='Admin')
            request.user.ebuio_member = True
            request.user.ebuio_admin = True
        else:
            request.user = AnonymousUser()

    # Caching
    cacheKey = None

    if 'cache_time' in meta:
        if meta['cache_time'] > 0:

            # by default, no cache by user
            useUser = False

            # If a logged user in needed, cache the result by user
            if ('only_logged_user' in meta and meta['only_logged_user']) or ('only_member_user' in meta and meta['only_member_user']) or ('only_admin_user' in meta and meta['only_admin_user']):
                useUser = True

            # If a value if present in meta, use it
            if 'cache_by_user' in meta:
                useUser = meta['cache_by_user']

            cacheKey = 'plutit-data-'

            # Add user info if needed
            if useUser:
                cacheKey += str(request.user.pk) + '-'

            # Add current query
            cacheKey += request.get_full_path()

            # Add current template (if the template changed, cache must be invalided)
            cacheKey += meta['template_tag']

    # Access

    # User must be logged ?
    if ('only_logged_user' in meta and meta['only_logged_user']):
        if not request.user.is_authenticated():
            return gen403('only_logged_user')

    # User must be member of the project ?
    if ('only_memeber_user' in meta and meta['only_memeber_user']):
        if not request.user.ebuio_member:
            return gen403('only_memeber_user')

    # User must be administrator of the project ?
    if ('only_admin_user' in meta and meta['only_admin_user']):
        if not request.user.ebuio_admin:
            return gen403('only_admin_user')

    # If we have to use cache, we try to find the result in cache
    if cacheKey is not None:
        result = cache.get(cacheKey, None)

        #We found a result, we can return it
        if result is not None:
            return HttpResponse(result)

    # Get template
    templateContent = plugIt.getTemplate(query, meta)

    if not templateContent:
        return gen404('template')

    # Build parameters
    getParameters = {}
    postParameters = {}
    files = {}

    # Copy GET parameters, excluding ebuio_*
    for v in request.GET:
        if v[:6] != 'ebuio_':
            val = request.GET.getlist(v)

            if len(val) == 1:
                getParameters[v] = val[0]
            else:
                getParameters[v] = val

    # If using post, copy post parameters and files. Excluding ebuio_*
    if request.method == 'POST':
        for v in request.POST:
            if v[:6] != 'ebuio_':
                val = request.POST.getlist(v)

                if len(val) == 1:
                    postParameters[v] = val[0]
                else:
                    postParameters[v] = val

        for v in request.FILES:
            if v[:6] != 'ebuio_':
                files[v] = request.FILES[v].chunks()

    # Add parameters requested by the server
    if 'user_info' in meta:
        for prop in meta['user_info']:

            # Test if the value exist, otherwise return None
            value = None
            if hasattr(request.user, prop):
                value = getattr(request.user, prop)

            # Add informations to get or post parameters, depending on the current method
            if request.method == 'POST':
                postParameters['ebuio_u_' + prop] = value
            else:
                getParameters['ebuio_u_' + prop] = value

    # Do the action
    data = plugIt.doAction(query, request.method == 'POST', getParameters, postParameters, files)

    if data is None:
        return gen404('data')

    # Add user information
    data['ebuio_u'] = request.user

    # Add current path
    data['ebuio_baseUrl'] = settings.PIAPI_BASEURI

    # Add userMode
    data['ebuio_userMode'] = request.session.get('plugit-standalone-usermode', 'ano')

    # Render it
    template = Template(templateContent)
    context = Context(data)

    # Add csrf information to the contact
    context.update(csrf(request))

    result = template.render(context)

    # Cache the result for future uses if requested
    if cacheKey is not None:
        cache.set(cacheKey, result, meta['cache_time'])

    return HttpResponse(result)


@cache_control(public=True, max_age=3600)
def media(request, path):
    """Ask the server for a media and return it to the client browser. Add cache headers of 1 hour"""
    (media, contentType) = plugIt.getMedia(path)

    if not media:  # No media returned
        raise Http404

    response = HttpResponse(media)
    response['Content-Type'] = contentType

    return response


def setUser(request):
    """In standalone mode, change the current user"""

    if not settings.PIAPI_STANDALONE:
        raise Http404

    request.session['plugit-standalone-usermode'] = request.GET.get('mode')

    return HttpResponse('')
