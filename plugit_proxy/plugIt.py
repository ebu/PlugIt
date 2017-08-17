# -*- coding: utf-8 -*-

import requests
import string
import random
import hashlib
from django.core.cache import cache
from urlparse import urlparse
from dateutil import parser
import datetime
from dateutil.tz import tzutc


class PlugIt():
    """Manage access to a specific server. Use caching for templates and meta information..."""

    PI_API_VERSION = '1'
    PI_API_NAME = 'EBUio-PlugIt'

    def __init__(self, baseURI, testIfOk=False):
        """Instance a new plugIt instance. Need the base URI of the server"""
        self.baseURI = baseURI
        self.cacheKey = 'plugit-' + hashlib.md5(baseURI).hexdigest()

        if testIfOk:
            # Check if everything is ok
            if not self.ping():
                raise Exception("Server doesn't reply to ping !")
            if not self.checkVersion():
                raise Exception("Not a correct PlugIt API version !")

    def doQuery(self, url, method='GET', getParmeters=None, postParameters=None, files=None, extraHeaders={}, session={}):
        """Send a request to the server and return the result"""

        # Build headers
        headers = {}

        if not postParameters:
            postParameters = {}

        for key, value in extraHeaders.iteritems():
            # Fixes #197 for values with utf-8 chars to be passed into plugit
            if isinstance(value, basestring):
                headers['X-Plugit-' + key] = value.encode('utf-8')
            else:
                headers['X-Plugit-' + key] = value

        for key, value in session.iteritems():
            headers['X-Plugitsession-' + key] = value
            if 'Cookie' not in headers:
                headers['Cookie'] = ''
            headers['Cookie'] += key + '=' + str(value) + '; '

        if method == 'POST':
            if not files:
                r = requests.post(self.baseURI + '/' + url, params=getParmeters, data=postParameters, stream=True, headers=headers)
            else:
                # Special way, for big files
                # Requests is not usable: https://github.com/shazow/urllib3/issues/51

                from poster.encode import multipart_encode, MultipartParam
                from poster.streaminghttp import register_openers
                import urllib2
                import urllib

                # Register the streaming http handlers with urllib2
                register_openers()

                # headers contains the necessary Content-Type and Content-Length
                # datagen is a generator object that yields the encoded parameters
                data = []
                for x in postParameters:
                    if isinstance(postParameters[x], list):
                        for elem in postParameters[x]:
                            data.append((x, elem))
                    else:
                        data.append((x, postParameters[x]))

                for f in files:
                    data.append((f, MultipartParam(f, fileobj=open(files[f].temporary_file_path(), 'rb'), filename=files[f].name)))

                datagen, headers_multi = multipart_encode(data)

                headers.update(headers_multi)

                if getParmeters:
                    get_uri = '?' + urllib.urlencode(getParmeters)
                else:
                    get_uri = ''

                # Create the Request object
                request = urllib2.Request(self.baseURI + '/' + url + get_uri, datagen, headers)

                re = urllib2.urlopen(request)

                from requests import Response

                r = Response()
                r.status_code = re.getcode()
                r.headers = dict(re.info())
                r.encoding = "application/json"
                r.raw = re.read()
                r._content = r.raw

                return r

        else:
            # Call the function based on the method.
            r = requests.request(method.upper(), self.baseURI + '/' + url, params=getParmeters, stream=True, headers=headers, allow_redirects=True)

        return r

    def ping(self):
        """Return true if the server successfully pinged"""

        randomToken = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(32))

        r = self.doQuery('ping?data=' + randomToken)

        if r.status_code == 200:  # Query ok ?
            if r.json()['data'] == randomToken:  # Token equal ?
                return True
        return False

    def checkVersion(self):
        """Check if the server use the same version of our protocol"""

        r = self.doQuery('version')

        if r.status_code == 200:  # Query ok ?
            data = r.json()

            if data['result'] == 'Ok' and data['version'] == self.PI_API_VERSION and data['protocol'] == self.PI_API_NAME:
                return True
        return False

    def newMail(self, data, message):
        """Send a mail to a plugit server"""
        r = self.doQuery('mail', method='POST', postParameters={'response_id': str(data), 'message': str(message)})

        if r.status_code == 200:  # Query ok ?
            data = r.json()

            return data['result'] == 'Ok'

        return False

    def getMedia(self, uri):
        """Return a tuple with a media and his content-type. Don't cache anything !"""

        r = self.doQuery('media/' + uri)

        if r.status_code == 200:
            content_type = 'application/octet-stream'

            if 'content-type' in r.headers:
                content_type = r.headers['content-type']

            cache_control = None

            if 'cache-control' in r.headers:
                cache_control = r.headers['cache-control']

            return (r.content, content_type, cache_control)
        else:
            return (None, None, None)

    def getMeta(self, uri):
        """Return meta information about an action. Cache the result as specified by the server"""

        action = urlparse(uri).path

        mediaKey = self.cacheKey + '_meta_' + action
        mediaKey = mediaKey.replace(' ', '__')

        meta = cache.get(mediaKey, None)

        # Nothing found -> Retrieve it from the server and cache it
        if not meta:

            r = self.doQuery('meta/' + uri)

            if r.status_code == 200:  # Get the content if there is not problem. If there is, template will stay to None
                meta = r.json()

            if 'expire' not in r.headers:
                expire = 5 * 60  # 5 minutes of cache if the server didn't specified anything
            else:
                expire = int((parser.parse(r.headers['expire']) - datetime.datetime.now(tzutc())).total_seconds())  # Use the server value for cache

            if expire > 0:  # Do the server want us to cache ?
                cache.set(mediaKey, meta, expire)

        return meta

    def getTemplate(self, uri, meta=None):
        """Return the template for an action. Cache the result. Can use an optional meta parameter with meta information"""

        if not meta:

            metaKey = self.cacheKey + '_templatesmeta_cache_' + uri

            meta = cache.get(metaKey, None)

            if not meta:
                meta = self.getMeta(uri)
                cache.set(metaKey, meta, 15)

        if not meta:  # No meta, can return a template
            return None

        # Let's find the template in the cache
        action = urlparse(uri).path

        templateKey = self.cacheKey + '_templates_' + action + '_' + meta['template_tag']
        template = cache.get(templateKey, None)

        # Nothing found -> Retrieve it from the server and cache it
        if not template:

            r = self.doQuery('template/' + uri)

            if r.status_code == 200:  # Get the content if there is not problem. If there is, template will stay to None
                template = r.content

            cache.set(templateKey, template, None)  # None = Cache forever

        return template

    def doAction(self, uri, method='GET', getParmeters=None, postParameters=None, files=None, extraHeaders={}, proxyMode=False, session={}):

        base_url = 'action/' if not proxyMode else ''

        r = self.doQuery(base_url + uri, method=method, getParmeters=getParmeters, postParameters=postParameters, files=files, extraHeaders=extraHeaders, session=session)

        class PlugItRedirect():
            """Object to perform a redirection"""
            def __init__(self, url, no_prefix=False):
                self.url = url
                self.no_prefix = no_prefix

        class PlugItFile():
            """Object to send a file"""
            def __init__(self, content, content_type, content_disposition=''):
                self.content = content
                self.content_type = content_type
                self.content_disposition = content_disposition

        class PlugItNoTemplate():
            """Object to display content without a template"""
            def __init__(self, content):
                self.content = content

        class PlugIt500():
            """Object to return a 500"""
            pass

        class PlugItSpecialCode():
            """Object to return a special status code"""
            def __init__(self, code):
                self.code = code

        if r.status_code == 500:
            return (PlugIt500(), {}, {})

        if r.status_code in [429, 404, 403, 401, 304]:
            return (PlugItSpecialCode(r.status_code), {}, {})

        if r.status_code == 200:  # Get the content if there is not problem. If there is, template will stay to None
            # {} is parsed as None (but should be an empty object)

            # Build list of elem to set from session
            session_to_set = {}

            for (key, value) in r.headers.iteritems():
                attr = 'ebuio-plugit-setsession-'
                if key.lower().startswith(attr):
                    session_to_set[key[len(attr):]] = value

            # Build list of headers to forward
            headers_to_set = {}

            for h in ['ETag', 'Access-Control-Allow-Origin', 'Access-Control-Allow-Credentials', 'Access-Control-Expose-Headers', 'Access-Control-Max-Age', 'Access-Control-Allow-Methods', 'Access-Control-Allow-Headers']:
                if h in r.headers:
                    headers_to_set[h] = r.headers[h]

            if 'ebuio-plugit-redirect' in r.headers:
                no_prefix = False

                if 'ebuio-plugit-redirect-noprefix' in r.headers:
                    no_prefix = r.headers['ebuio-plugit-redirect-noprefix'] == 'True'

                return (PlugItRedirect(r.headers['ebuio-plugit-redirect'], no_prefix), session_to_set, headers_to_set)

            if 'ebuio-plugit-itafile' in r.headers:

                if 'content-disposition' in r.headers:
                    content_disposition = r.headers['content-disposition']
                else:
                    content_disposition = ''

                return (PlugItFile(r.content, r.headers['Content-Type'], content_disposition), session_to_set, headers_to_set)

            if proxyMode and 'ebuio-plugit-notemplate' in r.headers:
                return (PlugItNoTemplate(r.content), session_to_set, headers_to_set)

            if proxyMode:
                return (r.content, session_to_set, headers_to_set)

            if not r.content or r.content == "{}":
                return ({}, session_to_set, headers_to_set)

            return (r.json(), session_to_set, headers_to_set)
        else:
            return (None, {}, {})
