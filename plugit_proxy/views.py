# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader_tags import BlockNode, ExtendsNode
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse, HttpResponseNotFound
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect, HttpResponseForbidden, HttpResponseServerError, JsonResponse
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_control
from django.template import Context, Template
from django.contrib.auth.models import User as DUser, AnonymousUser
from django.core.mail import EmailMessage


from plugIt import PlugIt


import json
import hashlib
import base64
import logging


logger = logging.getLogger(__name__)

# Standalone mode: Load the main plugit interface
if settings.PIAPI_STANDALONE:
    plugIt = PlugIt(settings.PIAPI_STANDALONE_URI)
    baseURI = settings.PIAPI_BASEURI


def getPlugItObject(hproPk):
    """Return the plugit object and the baseURI to use if not in standalone mode"""

    from hprojects.models import HostedProject

    try:
        hproject = HostedProject.objects.get(pk=hproPk)
    except (HostedProject.DoesNotExist, ValueError):
        try:
            hproject = HostedProject.objects.get(plugItCustomUrlKey=hproPk)
        except HostedProject.DoesNotExist:
            raise Http404

    if hproject.plugItURI == '' and not hproject.runURI:
        raise Http404
    plugIt = PlugIt(hproject.plugItURI)

    # Test if we should use custom key
    if hasattr(hproject, 'plugItCustomUrlKey') and hproject.plugItCustomUrlKey:
        baseURI = reverse('plugIt.views.main', args=(hproject.plugItCustomUrlKey, ''))
    else:
        baseURI = reverse('plugIt.views.main', args=(hproject.pk, ''))

    return (plugIt, baseURI, hproject)


def generate_user(mode=None, pk=None):
    """Return a false user for standalone mode"""

    user = None

    if mode == 'log' or pk == "-1":
        user = DUser(pk=-1, username='Logged', first_name='Logged', last_name='Hector', email='logeedin@plugit-standalone.ebuio')
        user.gravatar = 'https://www.gravatar.com/avatar/ebuio1?d=retro'
        user.ebuio_member = False
        user.ebuio_admin = False
        user.subscription_labels = []
    elif mode == 'mem' or pk == "-2":
        user = DUser(pk=-2, username='Member', first_name='Member', last_name='Luc', email='memeber@plugit-standalone.ebuio')
        user.gravatar = 'https://www.gravatar.com/avatar/ebuio2?d=retro'
        user.ebuio_member = True
        user.ebuio_admin = False
        user.subscription_labels = []
    elif mode == 'adm' or pk == "-3":
        user = DUser(pk=-3, username='Admin', first_name='Admin', last_name='Charles', email='admin@plugit-standalone.ebuio')
        user.gravatar = 'https://www.gravatar.com/avatar/ebuio3?d=retro'
        user.ebuio_member = True
        user.ebuio_admin = True
        user.subscription_labels = []
    elif mode == 'ano':
        user = AnonymousUser()
        user.email = 'nobody@plugit-standalone.ebuio'
        user.first_name = 'Ano'
        user.last_name = 'Nymous'
        user.ebuio_member = False
        user.ebuio_admin = False
        user.subscription_labels = []
    elif settings.PIAPI_STANDALONE and pk >= 0:
        # Generate an unknown user for compatibility reason in standalone mode
        user = DUser(pk=pk, username='Logged', first_name='Unknown', last_name='Other User', email='unknown@plugit-standalone.ebuio')
        user.gravatar = 'https://www.gravatar.com/avatar/unknown?d=retro'
        user.ebuio_member = False
        user.ebuio_admin = False
        user.subscription_labels = []

    if user:
        user.ebuio_orga_member = user.ebuio_member
        user.ebuio_orga_admin = user.ebuio_admin

    return user


class SimpleOrga():
    """Simple orga class"""
    pass


class SimpleUser():
    """Simple user class"""
    pass


def gen404(request, baseURI, reason):
    """Return a 404 error"""
    return HttpResponseNotFound(
        render_to_response('plugIt/404.html', {'context':
            {
                'reason': reason,
                'ebuio_baseUrl': baseURI,
                'ebuio_userMode': request.session.get('plugit-standalone-usermode', 'ano'),
            }
        }, context_instance=RequestContext(request)))


def gen500(request, baseURI):
    """Return a 500 error"""
    return HttpResponseServerError(
        render_to_response('plugIt/500.html', {
            'context': {
                'ebuio_baseUrl': baseURI,
                'ebuio_userMode': request.session.get('plugit-standalone-usermode', 'ano'),
            }
        }, context_instance=RequestContext(request)))


def gen403(request, baseURI, reason, project=None):
    """Return a 403 error"""
    orgas = None
    public_ask = False

    if not settings.PIAPI_STANDALONE:
        from organizations.models import Organization

        if project and project.plugItLimitOrgaJoinable:
            orgas = project.plugItOrgaJoinable.order_by('name').all()
        else:
            orgas = Organization.objects.order_by('name').all()

        rorgas = []

        # Find and exclude the visitor orga
        for o in orgas:
            if str(o.pk) == settings.VISITOR_ORGA_PK:
                public_ask = True
            else:
                rorgas.append(o)

        orgas = rorgas

    return HttpResponseForbidden(render_to_response('plugIt/403.html', {'context':
        {
            'reason': reason,
            'orgas': orgas,
            'public_ask': public_ask,
            'ebuio_baseUrl': baseURI,
            'ebuio_userMode': request.session.get('plugit-standalone-usermode', 'ano'),
            'ebuio_project': project
        }
    }, context_instance=RequestContext(request)))


def get_cache_key(request, meta, orgaMode, currentOrga):
    """Return the cache key to use"""

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

            cacheKey = '-'

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

    return cacheKey


def check_rights_and_access(request, meta):
    """Check if the user can access the page"""
    # User must be logged ?
    if ('only_logged_user' in meta and meta['only_logged_user']):
        if not request.user.is_authenticated():
            return gen403(request, baseURI, 'only_logged_user')

    # User must be member of the project ?
    if ('only_member_user' in meta and meta['only_member_user']):
        if not request.user.ebuio_member:
            return gen403(request, baseURI, 'only_member_user')

    # User must be administrator of the project ?
    if ('only_admin_user' in meta and meta['only_admin_user']):
        if not request.user.ebuio_admin:
            return gen403(request, baseURI, 'only_admin_user')

    # User must be member of the orga ?
    if ('only_orga_member_user' in meta and meta['only_orga_member_user']):
        if not request.user.ebuio_orga_member:
            return gen403(request, baseURI, 'only_orga_member_user')

    # User must be administrator of the orga ?
    if ('only_orga_admin_user' in meta and meta['only_orga_admin_user']):
        if not request.user.ebuio_orga_admin:
            return gen403(request, baseURI, 'only_orga_admin_user')

    # Remote IP must be in range ?
    if ('address_in_networks' in meta):
        if not is_requestaddress_in_networks(request, meta['address_in_networks']):
            return gen403(request, baseURI, 'address_in_networks')


def is_requestaddress_in_networks(request, networks):
    """Helper method to check if the remote real ip of a request is in a network"""
    from ipware.ip import get_real_ip, get_ip

    # Get the real IP, i.e. no reverse proxy, no nginx
    ip = get_real_ip(request)
    if not ip:
        ip = get_ip(request)
        if not ip:
            return False

    # For all networks
    for network in networks:
        if is_address_in_network(ip, network):
            return True

    return False


def is_address_in_network(ip, net):
    """Is an address in a network"""
    # http://stackoverflow.com/questions/819355/how-can-i-check-if-an-ip-is-in-a-network-in-python
    import socket
    import struct
    ipaddr = struct.unpack('=L', socket.inet_aton(ip))[0]
    netaddr, bits = net.split('/')
    if int(bits) == 0:
        return True
    net = struct.unpack('=L', socket.inet_aton(netaddr))[0]

    mask = ((2L << int(bits) - 1) - 1)

    return (ipaddr & mask) == (net & mask)


def find_in_cache(cacheKey):
    """Check if the content exists in cache and return it"""
    # If we have to use cache, we try to find the result in cache
    if cacheKey:

        data = cache.get('plugit-cache-' + cacheKey, None)

        # We found a result, we can return it
        if data:
            return (data['result'], data['menu'], data['context'])
    return (None, None, None)


def build_base_parameters(request):
    """Build the list of parameters to forward from the post and get parameters"""

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

    return (getParameters, postParameters, files)


def build_user_requested_parameters(request, meta):
    """Build the list of parameters requested by the plugit server"""

    postParameters = {}
    getParameters = {}
    files = {}

    # Add parameters requested by the server
    if 'user_info' in meta:
        for prop in meta['user_info']:

            # Test if the value exist, otherwise return None
            value = None
            if hasattr(request.user, prop) and prop in settings.PIAPI_USERDATA:
                value = getattr(request.user, prop)
            else:
                raise Exception('requested user attribute "%s", '
                                'does not exist or requesting is not allowed' % prop)

            # Add informations to get or post parameters, depending on the current method
            if request.method == 'POST':
                postParameters['ebuio_u_' + prop] = value
            else:
                getParameters['ebuio_u_' + prop] = value

    return (getParameters, postParameters, files)


def build_orga_parameters(request, orgaMode, currentOrga):
    postParameters = {}
    getParameters = {}
    files = {}

    # If orga mode, add the current orga pk
    if orgaMode and currentOrga:
        if request.method == 'POST':
            postParameters['ebuio_orgapk'] = currentOrga.pk
        else:
            getParameters['ebuio_orgapk'] = currentOrga.pk

    return (getParameters, postParameters, files)


def build_parameters(request, meta, orgaMode, currentOrga):
    """Return the list of get, post and file parameters to send"""

    postParameters = {}
    getParameters = {}
    files = {}

    def update_parameters(data):
        tmp_getParameters, tmp_postParameters, tmp_files = data

        getParameters.update(tmp_getParameters)
        postParameters.update(tmp_postParameters)
        files.update(tmp_files)

    update_parameters(build_base_parameters(request))
    update_parameters(build_user_requested_parameters(request, meta))
    update_parameters(build_orga_parameters(request, orgaMode, currentOrga))

    return (getParameters, postParameters, files)


def build_extra_headers(request, proxyMode, orgaMode, currentOrga):
    """Build the list of extra headers"""

    things_to_add = {}

    # If in proxymode, add needed infos to headers
    if proxyMode:

        # User
        for prop in settings.PIAPI_USERDATA:
            if hasattr(request.user, prop):
                things_to_add['user_' + prop] = getattr(request.user, prop)

        # Orga
        if orgaMode:
            things_to_add['orga_pk'] = currentOrga.pk
            things_to_add['orga_name'] = currentOrga.name
            things_to_add['orga_codops'] = currentOrga.ebu_codops

        # General
        things_to_add['base_url'] = baseURI

    if request and hasattr(request, 'META'):
        if 'REMOTE_ADDR' in request.META:
            things_to_add['remote-addr'] = request.META['REMOTE_ADDR']

        for meta_header, dest_header in [('HTTP_IF_NONE_MATCH', 'If-None-Match'), ('HTTP_ORIGIN', 'Origin'), ('HTTP_ACCESS_CONtROL_REQUEST_METHOD', 'Access-Control-Request-Method'), ('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', 'Access-Control-Request-Headers')]:
            if meta_header in request.META:
                things_to_add[dest_header] = request.META[meta_header]

    return things_to_add


def handle_special_cases(request, data, baseURI, meta):
    """Handle sepcial cases for returned values by the doAction function"""

    if request.method == 'OPTIONS':
        r = HttpResponse('')
        return r

    if data is None:
        return gen404(request, baseURI, 'data')

    if data.__class__.__name__ == 'PlugIt500':
        return gen500(request, baseURI)

    if data.__class__.__name__ == 'PlugItSpecialCode':
        r = HttpResponse('')
        r.status_code = data.code
        return r

    if data.__class__.__name__ == 'PlugItRedirect':
        url = data.url
        if not data.no_prefix:
            url = baseURI + url

        return HttpResponseRedirect(url)

    if data.__class__.__name__ == 'PlugItFile':
        response = HttpResponse(data.content, content_type=data.content_type)
        response['Content-Disposition'] = data.content_disposition

        return response

    if data.__class__.__name__ == 'PlugItNoTemplate':
        response = HttpResponse(data.content)
        return response

    if meta.get('json_only', None):  # Just send the json back
        # Return application/json if requested
        if 'HTTP_ACCEPT' in request.META and request.META['HTTP_ACCEPT'].find('json') != -1:
            return JsonResponse(data)

        # Return json data without html content type, since json was not
        # requiered
        result = json.dumps(data)
        return HttpResponse(result)

    if meta.get('xml_only', None):  # Just send the xml back
        return HttpResponse(data['xml'], content_type='application/xml')


def build_final_response(request, meta, result, menu, hproject, proxyMode, context):
    """Build the final response to send back to the browser"""

    if 'no_template' in meta and meta['no_template']:  # Just send the json back
        return HttpResponse(result)

    # TODO this breaks pages not using new template
    # Add sidebar toggler if plugit did not add by itself
    # if not "sidebar-toggler" in result:
    #     result = "<div class=\"menubar\"><div class=\"sidebar-toggler visible-xs\"><i class=\"ion-navicon\"></i></div></div>" + result

    # render the template into the whole page
    if not settings.PIAPI_STANDALONE:
        return render_to_response('plugIt/' + hproject.get_plugItTemplate_display(),
                                  {"project": hproject,
                                   "plugit_content": result,
                                   "plugit_menu": menu,
                                   'context': context},
                                  context_instance=RequestContext(request))

    if proxyMode:  # Force inclusion inside template
        return render_to_response('plugIt/base.html',
                                  {'plugit_content': result,
                                   "plugit_menu": menu,
                                   'context': context},
                                  context_instance=RequestContext(request))

    renderPlugItTemplate = 'plugItBase.html'
    if settings.PIAPI_PLUGITTEMPLATE:
        renderPlugItTemplate = settings.PIAPI_PLUGITTEMPLATE

    return render_to_response('plugIt/' + renderPlugItTemplate,
                              {"plugit_content": result,
                               "plugit_menu": menu,
                               'context': context},
                              context_instance=RequestContext(request))


def _get_node(template, context, name):
    '''
    taken originally from
    http://stackoverflow.com/questions/2687173/django-how-can-i-get-a-block-from-a-template
    '''
    for node in template:
        if isinstance(node, BlockNode) and node.name == name:
            return node.nodelist.render(context)
        elif isinstance(node, ExtendsNode):
            return _get_node(node.nodelist, context, name)

    # raise Exception("Node '%s' could not be found in template." % name)
    return ""


def render_data(context, templateContent, proxyMode, rendered_data, menukey='menubar'):
    """Render the template"""

    if proxyMode:
        # Update csrf_tokens
        csrf = unicode(context['csrf_token'])
        tag = u'{~__PLUGIT_CSRF_TOKEN__~}'
        rendered_data = unicode(rendered_data, 'utf-8').replace(tag, csrf)

        result = rendered_data  # Render in proxy mode
        menu = None  # Proxy mode plugit do not have menu

    else:
        # Render it
        template = Template(templateContent)
        result = template.render(context)
        menu = _get_node(template, context, menukey)

    return (result, menu)


def cache_if_needed(cacheKey, result, menu, context, meta):
    """Cache the result, if needed"""

    if cacheKey:

        # This will be a method in django 1.7
        flat_context = {}
        for d in context.dicts:
            flat_context.update(d)

        del flat_context['csrf_token']

        data = {'result': result, 'menu': menu, 'context': flat_context}

        cache.set('plugit-cache-' + cacheKey, data, meta['cache_time'])


def build_context(request, data, hproject, orgaMode, currentOrga, availableOrga):
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
        data['ebuio_orga'] = currentOrga

        # If not standalone mode, list the available orgas
        if not settings.PIAPI_STANDALONE:
            data['ebuio_orgas'] = []
            for (orga, _) in availableOrga:
                tmpOrga = SimpleOrga()
                tmpOrga.pk = orga.pk
                tmpOrga.name = orga.name
                tmpOrga.ebu_codops = orga.ebu_codops

                data['ebuio_orgas'].append(tmpOrga)

    context = Context(data)

    # Add csrf information to the contact
    context.update(csrf(request))

    # Add media urls
    context.update({'MEDIA_URL': settings.MEDIA_URL, 'STATIC_URL': settings.STATIC_URL})

    return context


def get_template(request, query, meta, proxyMode):
    """Return (if needed) the template to use"""

    templateContent = None

    if not proxyMode:

        templateContent = plugIt.getTemplate(query, meta)

        if not templateContent:
            return (None, gen404(request, baseURI, 'template'))

    return (templateContent, None)


def get_current_orga(request, hproject, availableOrga):
    """Return the current orga to use"""

    # If nothing available return 404
    if len(availableOrga) == 0:
        raise Http404

    # Find the current orga
    currentOrgaId = request.session.get('plugit-orgapk-' + str(hproject.pk), None)

    # If we don't have a current one select the first available
    if currentOrgaId is None:
        (tmpOrga, _) = availableOrga[0]
        currentOrgaId = tmpOrga.pk
    else:
        # If the current Orga is not among the available ones reset to the first one
        availableOrgaIds = [o.pk for (o, r) in availableOrga]
        if currentOrgaId not in availableOrgaIds:
            (tmpOrga, _) = availableOrga[0]
            currentOrgaId = tmpOrga.pk

    from organizations.models import Organization

    realCurrentOrga = get_object_or_404(Organization, pk=currentOrgaId)

    return realCurrentOrga


def update_session(request, session_to_set, hproPk):
    """Update the session with users-realted values"""

    for key, value in session_to_set.items():
        request.session['plugit_' + str(hproPk) + '_' + key] = value


def get_current_session(request, hproPk):
    """Get the current session value"""

    retour = {}

    base_key = 'plugit_' + str(hproPk) + '_'

    for key, value in request.session.iteritems():
        if key.startswith(base_key):
            retour[key[len(base_key):]] = value

    return retour


def main(request, query, hproPk=None, returnMenuOnly=False):
    """ Main method called for main page"""
    if settings.PIAPI_STANDALONE:
        global plugIt, baseURI

        # Check if settings are ok
        if settings.PIAPI_ORGAMODE and settings.PIAPI_REALUSERS:
            return gen404(request, baseURI,
                          "Configuration error. PIAPI_ORGAMODE and PIAPI_REALUSERS both set to True !")

        hproject = None
    else:
        (plugIt, baseURI, hproject) = getPlugItObject(hproPk)
        hproject.update_last_access(request.user)

    # Check for SSL Requirements and redirect to ssl if necessary
    if hproject and hproject.plugItRequiresSsl:
        if not request.is_secure():
            secure_url = 'https://{0}{1}'.format(request.get_host(), request.get_full_path())
            return HttpResponsePermanentRedirect(secure_url)

    orgaMode = None
    currentOrga = None
    plugItMenuAction = None
    availableOrga = []

    # If standalone mode, change the current user and orga mode based on parameters
    if settings.PIAPI_STANDALONE:

        if not settings.PIAPI_REALUSERS:
            currentUserMode = request.session.get('plugit-standalone-usermode', 'ano')

            request.user = generate_user(mode=currentUserMode)

            orgaMode = settings.PIAPI_ORGAMODE

            currentOrga = SimpleOrga()
            currentOrga.name = request.session.get('plugit-standalone-organame', 'EBU')
            currentOrga.pk = request.session.get('plugit-standalone-orgapk', '-1')
            currentOrga.ebu_codops = request.session.get('plugit-standalone-orgacodops', 'zzebu')
        else:
            request.user.ebuio_member = request.user.is_staff
            request.user.ebuio_admin = request.user.is_superuser
            request.user.subscription_labels = _get_subscription_labels(request.user, hproject)

        proxyMode = settings.PIAPI_PROXYMODE
        plugItMenuAction = settings.PIAPI_PLUGITMENUACTION

        # TODO Add STANDALONE Orgas here
        # availableOrga.append((orga, isAdmin))

        # Get meta, if not in proxy mode
        if not proxyMode:
            meta = plugIt.getMeta(query)

            if not meta:
                return gen404(request, baseURI, 'meta')
        else:
            meta = {}

    else:
        request.user.ebuio_member = hproject.isMemberRead(request.user)
        request.user.ebuio_admin = hproject.isMemberWrite(request.user)
        request.user.subscription_labels = _get_subscription_labels(request.user, hproject)
        orgaMode = hproject.plugItOrgaMode
        proxyMode = hproject.plugItProxyMode
        plugItMenuAction = hproject.plugItMenuAction

        # Get meta, if not in proxy mode
        if not proxyMode:
            meta = plugIt.getMeta(query)

            if not meta:
                return gen404(request, baseURI, 'meta')
        else:
            meta = {}

        if orgaMode:
            # List available orgas
            if request.user.is_authenticated():
                # If orga limited only output the necessary orgas to which the user has access
                if hproject and hproject.plugItLimitOrgaJoinable:
                    # Get List of Plugit Available Orgas first
                    projectOrgaIds = hproject.plugItOrgaJoinable.order_by('name').values_list('pk', flat=True)
                    for (orga, isAdmin) in request.user.getOrgas(distinct=True):
                        if orga.pk in projectOrgaIds:
                            availableOrga.append((orga, isAdmin))

                else:
                    availableOrga = request.user.getOrgas(distinct=True)

            if not availableOrga:
                # TODO HERE TO CHANGE PUBLIC
                if not meta.get('public'):  # Page is not public, raise 403
                    return gen403(request, baseURI, 'no_orga_in_orgamode', hproject)
            else:
                # Build the current orga
                realCurrentOrga = get_current_orga(request, hproject, availableOrga)

                currentOrga = SimpleOrga()

                currentOrga.pk = realCurrentOrga.pk
                currentOrga.name = realCurrentOrga.name
                currentOrga.ebu_codops = realCurrentOrga.ebu_codops

                # Get rights
                request.user.ebuio_orga_member = realCurrentOrga.isMember(request.user)
                request.user.ebuio_orga_admin = realCurrentOrga.isOwner(request.user)

    cacheKey = get_cache_key(request, meta, orgaMode, currentOrga)

    # Check access rights
    error = check_rights_and_access(request, meta)

    if error:
        return error

    # Check cache
    (cache, menucache, context) = find_in_cache(cacheKey)

    if cache:
        return build_final_response(request, meta, cache, menucache, hproject, proxyMode, context)

    # Build parameters
    getParameters, postParameters, files = build_parameters(request, meta, orgaMode, currentOrga)

    # Bonus headers
    things_to_add = build_extra_headers(request, proxyMode, orgaMode, currentOrga)

    current_session = get_current_session(request, hproPk)

    # Do the action
    (data, session_to_set, headers_to_set) = plugIt.doAction(query, request.method, getParameters, postParameters, files, things_to_add, proxyMode=proxyMode, session=current_session)

    update_session(request, session_to_set, hproPk)

    # Handle special case (redirect, etc..)
    spe_cases = handle_special_cases(request, data, baseURI, meta)
    if spe_cases:

        for header, value in headers_to_set.items():
            spe_cases[header] = value

        return spe_cases

    # Save data for proxyMode
    if proxyMode:
        rendered_data = data
        data = {}
    else:
        rendered_data = None

    # Get template
    (templateContent, templateError) = get_template(request, query, meta, proxyMode)

    if templateError:
        return templateError

    # Build the context
    context = build_context(request, data, hproject, orgaMode, currentOrga, availableOrga)

    # Render the result
    menu = None  # Some page may not have a menu
    (result, menu) = render_data(context, templateContent, proxyMode, rendered_data, plugItMenuAction)

    # Cache the result for future uses if requested
    cache_if_needed(cacheKey, result, menu, context, meta)

    # Return menu only : )
    if returnMenuOnly:
        return menu

    # Return the final response
    final = build_final_response(request, meta, result, menu, hproject, proxyMode, context)

    for header, value in headers_to_set.items():
        final[header] = value

    return final


def _get_subscription_labels(user, hproject):
    from users.models import TechUser

    if isinstance(user, TechUser):
        s = user.getActiveSubscriptionLabels(hproject, False)
        return s

    return []


@cache_control(public=True, max_age=3600)
def media(request, path, hproPk=None):
    """Ask the server for a media and return it to the client browser. Forward cache headers"""

    if not settings.PIAPI_STANDALONE:
        (plugIt, baseURI, _) = getPlugItObject(hproPk)
    else:
        global plugIt, baseURI

    (media, contentType, cache_control) = plugIt.getMedia(path)

    if not media:  # No media returned
        raise Http404

    response = HttpResponse(media)
    response['Content-Type'] = contentType
    response['Content-Length'] = len(media)

    if cache_control:
        response['Cache-Control'] = cache_control

    return response


def setUser(request):
    """In standalone mode, change the current user"""

    if not settings.PIAPI_STANDALONE or settings.PIAPI_REALUSERS:
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


def home(request, hproPk):
    """ Route the request to runURI if defined otherwise go to plugIt """

    if settings.PIAPI_STANDALONE:
        return main(request, '', hproPk)

    (plugIt, baseURI, hproject) = getPlugItObject(hproPk)
    if hproject.runURI:
        return HttpResponseRedirect(hproject.runURI)
    else:
        # Check if a custom url key is used
        if hasattr(hproject, 'plugItCustomUrlKey') and hproject.plugItCustomUrlKey:
            return HttpResponseRedirect(reverse('plugIt.views.main', args=(hproject.plugItCustomUrlKey, '')))

        return main(request, '', hproPk)


def api_home(request, key=None, hproPk=None):
    """Show the home page for the API with all methods"""

    if not check_api_key(request, key, hproPk):
        return HttpResponseForbidden

    return render_to_response('plugIt/api.html', {}, context_instance=RequestContext(request))


def api_user(request, userPk, key=None, hproPk=None):
    """Return information about an user"""

    if not check_api_key(request, key, hproPk):
        return HttpResponseForbidden

    if settings.PIAPI_STANDALONE:
        if not settings.PIAPI_REALUSERS:
            user = generate_user(pk=userPk)
            if user is None:
                return HttpResponseNotFound()
        else:
            user = get_object_or_404(DUser, pk=userPk)

        hproject = None
    else:
        from users.models import TechUser

        user = get_object_or_404(TechUser, pk=userPk)

        (_, _, hproject) = getPlugItObject(hproPk)

        user.ebuio_member = hproject.isMemberRead(user)
        user.ebuio_admin = hproject.isMemberWrite(user)
        user.subscription_labels = _get_subscription_labels(user, hproject)

    retour = {}

    # Append properties for the user data
    for prop in settings.PIAPI_USERDATA:
        if hasattr(user, prop):
            retour[prop] = getattr(user, prop)

    retour['id'] = str(retour['pk'])

    # Append the users organisation and access levels
    orgas = {}
    if user:
        limitedOrgas = []

        if hproject and hproject.plugItLimitOrgaJoinable:
            # Get List of Plugit Available Orgas first
            projectOrgaIds = hproject.plugItOrgaJoinable.order_by('name').values_list('pk', flat=True)
            for (orga, isAdmin) in user.getOrgas(distinct=True):
                if orga.pk in projectOrgaIds:
                    limitedOrgas.append((orga, isAdmin))
        elif hasattr(user, 'getOrgas'):
            limitedOrgas = user.getOrgas(distinct=True)

        # Create List
        orgas = [{'id': orga.pk, 'name': orga.name, 'codops': orga.ebu_codops, 'is_admin': isAdmin} for (orga, isAdmin)
                 in limitedOrgas]
    retour['orgas'] = orgas

    return HttpResponse(json.dumps(retour), content_type="application/json")


def api_user_uuid(request, userUuid, key=None, hproPk=None):
    """Return information about an user based on uuid"""

    if not check_api_key(request, key, hproPk):
        return HttpResponseForbidden

    # From UUID to Pk
    from users.models import TechUser

    user = get_object_or_404(TechUser, uuid=userUuid)

    (_, _, hproject) = getPlugItObject(hproPk)

    user.ebuio_member = hproject.isMemberRead(user)
    user.ebuio_admin = hproject.isMemberWrite(user)
    user.subscription_labels = _get_subscription_labels(user, hproject)

    return api_user(request, user.pk, key, hproPk)


def api_subscriptions(request, userPk, key=None, hproPk=None):
    """Return information about an user based on uuid"""

    if not check_api_key(request, key, hproPk):
        return HttpResponseForbidden

    # From UUID to Pk
    from users.models import TechUser

    user = get_object_or_404(TechUser, pk=userPk)

    (_, _, hproject) = getPlugItObject(hproPk)

    retour = user.getActiveSubscriptionLabels(hproject)

    return HttpResponse(json.dumps(retour), content_type="application/json")


def api_orga(request, orgaPk, key=None, hproPk=None):
    """Return information about an organization"""

    if not check_api_key(request, key, hproPk):
        return HttpResponseForbidden

    retour = {}

    if settings.PIAPI_STANDALONE:
        retour['pk'] = orgaPk
        if orgaPk == "-1":
            retour['name'] = 'EBU'
            retour['codops'] = 'zzebu'
        if orgaPk == "-2":
            retour['name'] = 'RTS'
            retour['codops'] = 'chrts'
        if orgaPk == "-3":
            retour['name'] = 'BBC'
            retour['codops'] = 'gbbbc'
        if orgaPk == "-4":
            retour['name'] = 'CNN'
            retour['codops'] = 'uscnn'

    else:
        from organizations.models import Organization

        orga = get_object_or_404(Organization, pk=orgaPk)

        retour['pk'] = orga.pk
        retour['name'] = orga.name
        retour['codops'] = orga.ebu_codops

    return HttpResponse(json.dumps(retour), content_type="application/json")


def api_get_project_members(request, key=None, hproPk=True):
    """Return the list of project members"""

    if not check_api_key(request, key, hproPk):
        return HttpResponseForbidden

    if settings.PIAPI_STANDALONE:
        if not settings.PIAPI_REALUSERS:
            users = [generate_user(pk="-1"), generate_user(pk="-2"), generate_user(pk="-3")]
        else:
            users = DUser.object.all()
    else:

        (_, _, hproject) = getPlugItObject(hproPk)

        users = []

        for u in hproject.getMembers():
            u.ebuio_member = True
            u.ebuio_admin = hproject.isMemberWrite(u)
            u.subscription_labels = _get_subscription_labels(u, hproject)
            users.append(u)

    liste = []

    for u in users:

        retour = {}

        for prop in settings.PIAPI_USERDATA:
            if hasattr(u, prop):
                retour[prop] = getattr(u, prop)

        retour['id'] = str(retour['pk'])

        liste.append(retour)

    return HttpResponse(json.dumps({'members': liste}), content_type="application/json")


def generic_send_mail(sender, dests, subject, message, key, origin='', html_message=False):
    """Generic mail sending function"""

    # If no EBUIO Mail settings have been set, then no e-mail shall be sent
    if settings.EBUIO_MAIL_SECRET_KEY and settings.EBUIO_MAIL_SECRET_HASH:
        headers = {}

        if key:
            from Crypto.Cipher import AES

            hash_key = hashlib.sha512(key + settings.EBUIO_MAIL_SECRET_HASH).hexdigest()[30:42]

            encrypter = AES.new(((settings.EBUIO_MAIL_SECRET_KEY) * 32)[:32], AES.MODE_CFB, '87447JEUPEBU4hR!')
            encrypted_key = encrypter.encrypt(hash_key + ':' + key)

            base64_key = base64.urlsafe_b64encode(encrypted_key)

            headers = {'Reply-To': settings.MAIL_SENDER.replace('@', '+' + base64_key + '@')}

        msg = EmailMessage(subject, message, sender, dests, headers=headers)
        if html_message:
            msg.content_subtype = "html"  # Main content is now text/html
        msg.send(fail_silently=False)

        try:
            from main.models import MailSend

            MailSend(dest=','.join(dests), subject=subject, sender=sender, message=message, origin=origin).save()

        except ImportError:
            pass
    else:
        logger.debug(
            "E-Mail notification not sent, since no EBUIO_MAIL_SECRET_KEY and EBUIO_MAIL_SECRET_HASH set in settingsLocal.py.")


@csrf_exempt
def api_send_mail(request, key=None, hproPk=None):
    """Send a email. Posts parameters are used"""

    if not check_api_key(request, key, hproPk):
        return HttpResponseForbidden

    sender = request.POST.get('sender', settings.MAIL_SENDER)
    dests = request.POST.getlist('dests')
    subject = request.POST['subject']
    message = request.POST['message']
    html_message = request.POST.get('html_message')

    if html_message and html_message.lower() == 'false':
        html_message = False

    if 'response_id' in request.POST:
        key = hproPk + ':' + request.POST['response_id']
    else:
        key = None

    generic_send_mail(sender, dests, subject, message, key, 'PlugIt API (%s)' % (hproPk or 'StandAlone',), html_message)

    return HttpResponse(json.dumps({}), content_type="application/json")


def api_orgas(request, key=None, hproPk=None):
    """Return the list of organizations pk"""

    if not check_api_key(request, key, hproPk):
        return HttpResponseForbidden

    list_orgas = []

    if settings.PIAPI_STANDALONE:
        list_orgas = [{'id': -1, 'name': 'EBU', 'codops': 'ZZEBU'},
                      {'id': -2, 'name': 'RTS', 'codops': 'CHRTS'},
                      {'id': -3, 'name': 'BBC', 'codops': 'GBEBU'},
                      {'id': -4, 'name': 'CNN', 'codops': 'USCNN'}]

    else:
        from organizations.models import Organization

        (_, _, hproject) = getPlugItObject(hproPk)

        if hproject and hproject.plugItLimitOrgaJoinable:
            orgas = hproject.plugItOrgaJoinable.order_by('name').all()
        else:
            orgas = Organization.objects.order_by('name').all()

        list_orgas = [{'id': orga.pk, 'name': orga.name, 'codops': orga.ebu_codops} for orga in orgas]

    retour = {'data': list_orgas}

    return HttpResponse(json.dumps(retour), content_type="application/json")


@csrf_exempt
def api_ebuio_forum(request, key=None, hproPk=None):
    """Create a topic on the forum of the ioproject. EBUIo only !"""

    if not check_api_key(request, key, hproPk):
        return HttpResponseForbidden

    if settings.PIAPI_STANDALONE:
        return HttpResponse(json.dumps({'error': 'no-on-ebuio'}), content_type="application/json")

    (_, _, hproject) = getPlugItObject(hproPk)

    error = ''

    subject = request.POST.get('subject')
    author_pk = request.POST.get('author')
    message = request.POST.get('message')
    tags = request.POST.get('tags', '')

    if not subject:
        error = 'no-subject'
    if not author_pk:
        error = 'no-author'
    else:
        try:
            from users.models import TechUser

            author = TechUser.objects.get(pk=author_pk)
        except TechUser.DoesNotExist:
            error = 'author-no-found'

    if not message:
        error = 'no-message'

    if error:
        return HttpResponse(json.dumps({'error': error}), content_type="application/json")

    # Create the topic
    from discuss.models import Post, PostTag

    if tags:
        real_tags = []
        for tag in tags.split(','):
            (pt, __) = PostTag.objects.get_or_create(tag=tag)
            real_tags.append(str(pt.pk))

        tags = ','.join(real_tags)

    post = Post(content_object=hproject, who=author, score=0, title=subject, text=message)
    post.save()

    from app.tags_utils import update_object_tag

    update_object_tag(post, PostTag, tags)

    post.send_email()

    # Return the URL
    return HttpResponse(json.dumps({'result': 'ok',
                                    'url': settings.EBUIO_BASE_URL + reverse('hprojects.views.forum_topic',
                                                                             args=(hproject.pk, post.pk))}),
                        content_type="application/json")


def api_ebuio_forum_get_topics_by_tag_for_user(request, key=None, hproPk=None, tag=None, userPk=None):
    """Return the list of topics using the tag pk"""

    # Check API key (in order to be sure that we have a valid one and that's correspond to the project
    if not check_api_key(request, key, hproPk):
        return HttpResponseForbidden

    if settings.PIAPI_STANDALONE:
        return HttpResponse(json.dumps({'error': 'no-on-ebuio'}), content_type="application/json")

    # We get the plugit object representing the project
    (_, _, hproject) = getPlugItObject(hproPk)

    # We get the user and we check his rights
    author_pk = request.GET.get('u')
    if author_pk and author_pk.isdigit():
        try:
            from users.models import TechUser

            user = TechUser.objects.get(pk=author_pk)
        except TechUser.DoesNotExist:
            error = 'user-no-found'
            user = generate_user(mode='ano')
    else:
        user = generate_user(mode='ano')

    if not hproject.discuss_can_display_posts(user):
        return HttpResponseForbidden

    # Verify the existence of the tag
    if not tag:
        raise Http404

    # We get the posts (only topics ones-the parent) related to the project and to the tag.
    # We dont' take the deleted ones.
    from discuss.models import Post

    posts = Post.objects.filter(is_deleted=False).filter(object_id=hproPk).filter(tags__tag=tag).order_by('-when')

    # We convert the posts list to json
    posts_json = [
        {'id': post.id, 'link': post.discuss_get_forum_topic_link(), 'subject': post.title, 'author': post.who_id,
         'when': post.when.strftime('%a, %d %b %Y %H:%M GMT'), 'score': post.score,
         'replies_number': post.direct_subposts_size()} for post in posts]

    return HttpResponse(json.dumps({'data': posts_json}), content_type="application/json")
