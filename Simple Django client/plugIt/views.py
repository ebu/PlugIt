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
from django.core.urlresolvers import reverse


from django.db.models import Q

from plugIt import PlugIt

from django.views.decorators.cache import cache_control

from django.template import Context, Template
from django.core.context_processors import csrf

from django.core.cache import cache

from django.contrib.auth.models import User as DUser, AnonymousUser

import json


# Standalone mode: Load the main plugit interface
if settings.PIAPI_STANDALONE:
    plugIt = PlugIt(settings.PIAPI_STANDALONE_URI)
    baseURI = settings.PIAPI_BASEURI

def getPlugItObject(hproPk):
    """Return the plugit object and the baseURI to use if not in standalone mode"""

    from hprojects.models import HostedProject
    hproject = get_object_or_404(HostedProject, pk=hproPk)
    if hproject.plugItURI == '':
        raise Http404
    plugIt = PlugIt(hproject.plugItURI)
    baseURI = reverse('plugIt.views.main', args=(hproject.pk, ''))

    return (plugIt, baseURI, hproject)

def generate_user(mode=None, pk=None):
    """Return a false user for standalone mode"""

    user = None

    if mode == 'log' or pk == "-1":
        user = DUser(pk=-1, username='Logged', first_name='Logged', last_name='Hector', email='logeedin@plugit-standalone.ebuio')
        user.ebuio_member = False
        user.ebuio_admin = False
    elif mode == 'mem' or pk == "-2":
        user = DUser(pk=-2, username='Member', first_name='Member', last_name='Luc', email='memeber@plugit-standalone.ebuio')
        user.ebuio_member = True
        user.ebuio_admin = False
    elif mode == 'adm' or pk == "-3":
        user = DUser(pk=-3, username='Admin', first_name='Admin', last_name='Charles', email='admin@plugit-standalone.ebuio')
        user.ebuio_member = True
        user.ebuio_admin = True
    elif mode == 'ano':
        user = AnonymousUser()
        user.email = 'nobody@plugit-standalone.ebuio'
        user.first_name = 'Ano'
        user.last_name = 'Nymous'
        user.ebuio_member = False
        user.ebuio_admin = False

    user.ebuio_orga_member = user.ebuio_member
    user.ebuio_orga_admin = user.ebuio_admin        

    return user


class SimpleOrga():
    """Simple orga class"""
    pass

class SimpleUser():
    """Simple user class"""
    pass

def main(request, query, hproPk=None):

    def gen404(reason):
        """Return a 404 error"""
        return HttpResponseNotFound(render_to_response('plugIt/404.html', {'reason': reason, 'ebuio_baseUrl':  baseURI, 'ebuio_userMode': request.session.get('plugit-standalone-usermode', 'ano')}, context_instance=RequestContext(request)))

    def gen403(reason):
        """Return a 403 error"""
        return HttpResponseNotFound(render_to_response('plugIt/403.html', {'reason': reason, 'ebuio_baseUrl':  baseURI, 'ebuio_userMode': request.session.get('plugit-standalone-usermode', 'ano')}, context_instance=RequestContext(request)))

    if not settings.PIAPI_STANDALONE:
        (plugIt, baseURI, hproject) = getPlugItObject(hproPk)
    else:
        global plugIt, baseURI

        # Check if settings are ok
        if settings.PIAPI_ORGAMODE and settings.PIAPI_REALUSERS:
            return gen404("Configuration error. PIAPI_ORGAMODE and PIAPI_REALUSERS both set to True !")

    # Get meta
    meta = plugIt.getMeta(query)

    if not meta:
        return gen404('meta')

    ## If standalone mode, change the current user and orga mode based on parameters
    if settings.PIAPI_STANDALONE:

        if not settings.PIAPI_REALUSERS:
            currentUserMode = request.session.get('plugit-standalone-usermode', 'ano')
            
            request.user = generate_user(mode=currentUserMode)      

            orgaMode = settings.PIAPI_ORGAMODE

            currentOrga = SimpleOrga()
            currentOrga.name = request.session.get('plugit-standalone-organame', 'EBU')
            currentOrga.pk = request.session.get('plugit-standalone-orgapk', '-1')
        else:
            request.user.ebuio_member = request.user.is_staff
            request.user.ebuio_admin = request.user.is_superuser
            orgaMode = None

    else:
        request.user.ebuio_member = hproject.isMemberRead(request.user)
        request.user.ebuio_admin = hproject.isMemberWrite(request.user)
        orgaMode = hproject.plugItOrgaMode

        if orgaMode:

            # List available orgas
            if request.user.is_authenticated():
                availableOrga = request.user.getOrgas()
            else:
                availableOrga = []

            if not availableOrga:
                return gen403('no_orga_in_orgamode')

            # Find the current orga
            currentOrgaId = request.session.get('plugit-orgapk-' + str(hproject.pk), None)

            if currentOrgaId is None:
                (tmpOrga, _) = availableOrga[0]
                currentOrgaId = tmpOrga.pk

            from organizations.models import Organization
            realCurrentOrga = get_object_or_404(Organization, pk=currentOrgaId)

            # Build the current orga
            currentOrga = SimpleOrga()

            currentOrga.pk = realCurrentOrga.pk
            currentOrga.name = realCurrentOrga.name

            # Get rights
            request.user.ebuio_orga_member = realCurrentOrga.isMember(request.user)
            request.user.ebuio_orga_admin = realCurrentOrga.isOwner(request.user)


    # Caching
    cacheKey = None

    if 'cache_time' in meta:
        if meta['cache_time'] > 0:

            # by default, no cache by user
            useUser = False

            # If a logged user in needed, cache the result by user
            if ('only_logged_user' in meta and meta['only_logged_user']) or \
                ('only_member_user' in meta and meta['only_member_user']) or \
                ('only_admin_user' in meta and meta['only_admin_user']) or \
                ('only_orga_member_user' in meta and meta['only_orga_member_user']) or \
                ('only_orga_admin_user' in meta and meta['only_orga_admin_user']):
                useUser = True

            # If a value if present in meta, use it
            if 'cache_by_user' in meta:
                useUser = meta['cache_by_user']

            cacheKey = 'plutit-data-'

            # Add user info if needed
            if useUser:
                cacheKey += str(request.user.pk) + 'usr-'

            # Add orga
            if orgaMode:
                cacheKey += str(currentOrga.pk) + 'org-'

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

    # User must be member of the orga ?
    if ('only_orga_memeber_user' in meta and meta['only_orga_memeber_user']):
        if not request.user.ebuio_orga_member:
            return gen403('only_orga_memeber_user')

    # User must be administrator of the orga ?
    if ('only_orga_admin_user' in meta and meta['only_orga_admin_user']):
        if not request.user.ebuio_orga_admin:
            return gen403('only_orga_admin_user')

    # If we have to use cache, we try to find the result in cache
    if cacheKey is not None:
        result = cache.get(cacheKey, None)

        #We found a result, we can return it
        if result is not None:
            return HttpResponse(result)

   

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
                files[v] = request.FILES[v]  # .chunks()

    # Add parameters requested by the server
    if 'user_info' in meta:
        for prop in meta['user_info']:

            # Test if the value exist, otherwise return None
            value = None
            if hasattr(request.user, prop) and prop in settings.PIAPI_USERDATA:
                value = getattr(request.user, prop)

            # Add informations to get or post parameters, depending on the current method
            if request.method == 'POST':
                postParameters['ebuio_u_' + prop] = value
            else:
                getParameters['ebuio_u_' + prop] = value

    # If orga mode, add the current orga pk
    if orgaMode:
        if request.method == 'POST':
            postParameters['ebuio_orgapk'] = currentOrga.pk
        else:
            getParameters['ebuio_orgapk'] = currentOrga.pk


    # Do the action
    data = plugIt.doAction(query, request.method, getParameters, postParameters, files)

    if data is None:
        return gen404('data')

    if data.__class__.__name__ == 'PlugItRedirect':
        url = data.url
        if not data.no_prefix:
            url = baseURI + url

        return HttpResponseRedirect(url)

    if data.__class__.__name__ == 'PlugItFile':
        response = HttpResponse(data.content, content_type=data.content_type)
        response['Content-Disposition'] = data.content_disposition

        return response

    # Get template, if needed
    if not('json_only' in meta and meta['json_only']):

        templateContent = plugIt.getTemplate(query, meta)

        if not templateContent:
            return gen404('template')

    if 'json_only' in meta and meta['json_only']:  # Just send the json back
        result = json.dumps(data)
    else:

        # Return only wanted properties about the user
        data['ebuio_u'] = SimpleUser()
        for prop in settings.PIAPI_USERDATA:
            if hasattr(request.user, prop):
                setattr(data['ebuio_u'], prop, getattr(request.user, prop))

        data['ebuio_u'].id = str(data['ebuio_u'].pk)

        # Add current path
        data['ebuio_baseUrl'] = baseURI

        # Add userMode
        if settings.PIAPI_STANDALONE:
            data['ebuio_userMode'] = request.session.get('plugit-standalone-usermode', 'ano')
            data['ebuio_realUsers'] = settings.PIAPI_REALUSERS
        else:
            data['ebuio_hpro_name'] = hproject.name
            data['ebuio_hpro_pk'] = hproject.pk
            from app.utils import create_secret
            data['ebuio_hpro_key'] = create_secret(str(hproject.pk), hproject.name, str(request.user.pk))

        # Add orga mode and orga
        data['ebuio_orgamode'] = orgaMode

        if orgaMode:
            data['ebuio_orga']  = currentOrga

            # If not standalone mode, list the available orgas
            if not settings.PIAPI_STANDALONE: 
                data['ebuio_orgas']  = []
                for (orga, _) in availableOrga:
                    tmpOrga = SimpleOrga()
                    tmpOrga.pk = orga.pk
                    tmpOrga.name = orga.name
                    data['ebuio_orgas'].append(tmpOrga)


        # Render it
        template = Template(templateContent)
        context = Context(data)

        # Add csrf information to the contact
        context.update(csrf(request))

        # Add media urls
        context.update({'MEDIA_URL': settings.MEDIA_URL, 'STATIC_URL': settings.STATIC_URL})

        result = template.render(context)

    # Cache the result for future uses if requested
    if cacheKey is not None:
        cache.set(cacheKey, result, meta['cache_time'])

    return HttpResponse(result)


@cache_control(public=True, max_age=3600)
def media(request, path, hproPk=None):
    """Ask the server for a media and return it to the client browser. Add cache headers of 1 hour"""

    if not settings.PIAPI_STANDALONE:
        (plugIt, baseURI, _) = getPlugItObject(hproPk)
    else:
        global plugIt, baseURI

    (media, contentType) = plugIt.getMedia(path)

    if not media:  # No media returned
        raise Http404

    response = HttpResponse(media)
    response['Content-Type'] = contentType

    return response


def setUser(request):
    """In standalone mode, change the current user"""

    if not settings.PIAPI_STANDALONE and not settings.PIAPI_REALUSERS:
        raise Http404

    request.session['plugit-standalone-usermode'] = request.GET.get('mode')

    return HttpResponse('')

def setOrga(request, hproPk=None):
    """Change the current orga"""

    if settings.PIAPI_STANDALONE:
        request.session['plugit-standalone-organame'] = request.GET.get('name')
        request.session['plugit-standalone-orgapk'] = request.GET.get('pk')
    else:


        (_, _, hproject) = getPlugItObject(hproPk)

        from organizations.models import Organization

        orga = get_object_or_404(Organization, pk=request.GET.get('orga'))


        if request.user.is_superuser or orga.isMember(request.user) or orga.isOwner(request.user):
            request.session['plugit-orgapk-' + str(hproject.pk)] = orga.pk

        return HttpResponse('')

def check_api_key(request, key, hproPk):
    """Check if an API key is valid"""

    if settings.PIAPI_STANDALONE:
        return True

    (_, _, hproject) = getPlugItObject(hproPk)

    if not hproject:
        return False

    if hproject.plugItApiKey is None or hproject.plugItApiKey == '':
        return False

    return hproject.plugItApiKey == key



def api_home(request, key=None, hproPk=None):
    """Show the home page for the API with all methods"""

    if not check_api_key(request, key, hproPk):
        raise Http404
    
    return render_to_response('plugIt/api.html', {}, context_instance=RequestContext(request))

def api_user(request, userPk, key=None, hproPk=None):
    """Return information about an user"""

    if not check_api_key(request, key, hproPk):
        raise Http404

    if settings.PIAPI_STANDALONE:
        if not settings.PIAPI_REALUSERS:
            user = generate_user(pk=userPk)
            if user is None:
                raise Http404
        else:
            user = get_object_or_404(User, pk=userPk)
    else:
        from users.models import TechUser
        user = get_object_or_404(TechUser, pk=userPk)

        (_, _, hproject) = getPlugItObject(hproPk)

        user.ebuio_member = hproject.isMemberRead(user)
        user.ebuio_admin = hproject.isMemberWrite(user)  

    retour = {}

    for prop in settings.PIAPI_USERDATA:
        retour[prop] = getattr(user, prop)
    
    retour['id'] = str(retour['pk'])

    return HttpResponse(json.dumps(retour), content_type="application/json") 

def api_orga(request, orgaPk, key=None, hproPk=None):
    """Return information about an organization"""

    if not check_api_key(request, key, hproPk):
        raise Http404

    retour = {}

    if settings.PIAPI_STANDALONE:
        retour['pk'] = orgaPk
        if orgaPk == "-1":
            retour['name'] = 'EBU'
        if orgaPk == "-2":
            retour['name'] = 'RTS'
        if orgaPk == "-3":
            retour['name'] = 'BBC'
        if orgaPk == "-4":
            retour['name'] = 'CNN'

    else:
        from organizations.models import Organization

        orga = get_object_or_404(Organization, pk=orgaPk)

        retour['pk'] = orga.pk
        retour['name'] = orga.name


    return HttpResponse(json.dumps(retour), content_type="application/json") 