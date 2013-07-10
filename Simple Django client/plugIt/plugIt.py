#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import string
import random
import hashlib
from django.core.cache import cache
from urlparse import urlparse
from dateutil import parser
import datetime
from dateutil.tz import *


class PlugIt():
    """Manage access to a specific server. Use caching for templates and meta information..."""

    PI_API_VERSION = '1'
    PI_API_NAME = 'EBUio-PlugIt'

    def __init__(self, baseURI):
        """Instance a new plugIt instance. Need the base URI of the server"""
        self.baseURI = baseURI
        self.cacheKey = 'plugit-' + hashlib.md5(baseURI).hexdigest()

        #Check if everything is ok
        if not self.ping():
            raise Exception("Server doesn't reply to ping !")
        if not self.checkVersion():
            raise Exception("Not a correct PlugIt API version !")

    def doQuery(self, url, usePost=False, getParmeters=None, postParameters=None, files=None):
        """Send a request to the server and return the result"""

        if usePost:
            r = requests.post(self.baseURI + '/' + url, params=getParmeters, data=postParameters, files=files)
        else:
            r = requests.get(self.baseURI + '/' + url, params=getParmeters)

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

    def getMedia(self, uri):
        """Return a tuple with a media and his content-type. Don't cache anything !"""

        r = self.doQuery('media/' + uri)

        if r.status_code == 200:
            return (r.content, r.headers['content-type'])
        else:
            return None

    def getMeta(self, uri):
        """Return meta information about an action. Cache the result as specified by the server"""

        action = urlparse(uri).path

        mediaKey = self.cacheKey + '_meta_' + action

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
            meta = self.getMeta(uri)

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

    def doAction(self, uri, usePost=False, getParmeters=None, postParameters=None, files=None):
        r = self.doQuery('action/' + uri, usePost=usePost, getParmeters=getParmeters, postParameters=postParameters, files=files)

        if r.status_code == 200:  # Get the content if there is not problem. If there is, template will stay to None
            # {} is parsed as None (but should be an empty object)

            if r.content == "{}":
                return {}
            return r.json()
        else:
            return None
