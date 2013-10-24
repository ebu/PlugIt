#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, send_from_directory, make_response, abort, send_file
from flask.views import View

import actions
from utils import md5Checksum, PlugItRedirect, PlugItSendFile

from datetime import datetime, timedelta


# Global parameters
DEBUG = True

# PlugIt Parameters

# PI_META_CACHE specify the number of seconds meta informations should be cached
PI_META_CACHE = 0 if DEBUG else 5 * 60  # 5 minutes

# Allow the API to be located at another endpoint (to share call with another API)
PI_BASE_URL = '/'

# IP allowed to use the PlugIt API.
PI_ALLOWED_NETWORKS = ['127.0.0.1/32']

## Does not edit code bellow !

# API version parameters
PI_API_VERSION = '1'
PI_API_NAME = 'EBUio-PlugIt'


app = Flask(__name__, static_folder='media', static_url_path=PI_BASE_URL+'media')


def check_ip(request):

    def addressInNetwork(ip, net):
        "Is an address in a network"
        #http://stackoverflow.com/questions/819355/how-can-i-check-if-an-ip-is-in-a-network-in-python
        import socket
        import struct
        ipaddr = struct.unpack('=L', socket.inet_aton(ip))[0]
        netaddr, bits = net.split('/')
        if int(bits) == 0:
            return True
        netmask = struct.unpack('=L', socket.inet_aton(netaddr))[0] & ((2L << int(bits)-1) - 1)
        return ipaddr & netmask == netmask

    for net in PI_ALLOWED_NETWORKS:
        if addressInNetwork(request.remote_addr, net):
            return True
    # Ip not found
    abort(404)
    return False


@app.route(PI_BASE_URL + "ping")
def ping():
    """The ping method: Just return the data provided"""

    if not check_ip(request):
        return

    return jsonify(data=request.args.get('data', ''))


@app.route(PI_BASE_URL + "version")
def version():
    """The version method: Return current information about the version"""
    return jsonify(result='Ok', version=PI_API_VERSION, protocol=PI_API_NAME)


class MetaView(View):
    """The dynamic view (based on the current action) for the /meta method"""

    def __init__(self, action):
        self.action = action

    def dispatch_request(self, *args, **kwargs):

        if not check_ip(request):
            return

        objResponse = {}

        # Template information
        objResponse['template_tag'] = ("" if self.action.pi_api_template == "" else
                                       md5Checksum('templates/' + self.action.pi_api_template))

        for attribute in (u'only_logged_user', u'only_member_user', u'only_admin_user',
                          u'only_orga_member_user', u'only_orga_admin_user',  # User restrictions
                          u'cache_time', u'cache_by_user',                    # Cache information
                          u'user_info', u'json_only'):                        # Requested user infos + JSON-only
            if hasattr(self.action, u'pi_api_' + attribute):
                objResponse[attribute] = getattr(self.action, u'pi_api_' + attribute)

        # Add the cache headers
        response = make_response(jsonify(objResponse))

        expires = datetime.utcnow() + timedelta(seconds=PI_META_CACHE)
        expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")

        response.headers['Expire'] = expires
        response.headers['Cache-Control'] = 'public, max-age=' + str(PI_META_CACHE)

        # Return the final response
        return response


class TemplateView(View):
    """The dynamic view (based on the current action) for the /template method"""

    def __init__(self, action):
        self.action = action

    def dispatch_request(self, *args, **kwargs):

        if not check_ip(request):
            return

        # We just return the content of the template
        return send_from_directory('templates/', self.action.pi_api_template)


class ActionView(View):
    """The dynamic view (based on the current action) for the /action method"""

    def __init__(self, action):
        self.action = action

    def dispatch_request(self, *args, **kwargs):

        if not check_ip(request):
            return

        # Call the action
        result = self.action(request, *args, **kwargs)

        # Is it a redirect ?
        if isinstance(result, PlugItRedirect):
            response = make_response("")
            response.headers['EbuIo-PlugIt-Redirect'] = result.url
            if result.no_prefix:
                response.headers['EbuIo-PlugIt-Redirect-NoPrefix'] = 'True'
            return response
        elif isinstance(result, PlugItSendFile):
            response = send_file(result.filename, mimetype=result.mimetype, as_attachment=result.as_attachment, attachment_filename=result.attachment_filename)
            response.headers['EbuIo-PlugIt-ItAFile'] = 'True'
            return response

        return jsonify(result)


# Register the 3 URLs (meta, template, action) for each actions
# We test for each element in the module actions if it's an action (added by the decorator in utils)
for act in dir(actions):
    obj = getattr(actions, act)
    if hasattr(obj, 'pi_api_action') and obj.pi_api_action:
        # We found an action and we can now add it to our routes

        # Meta
        app.add_url_rule(PI_BASE_URL + 'meta' + obj.pi_api_route, view_func=MetaView.as_view('meta_' + act, action=obj))

        # Template
        app.add_url_rule(PI_BASE_URL + 'template' + obj.pi_api_route, view_func=TemplateView.as_view('template_' + act, action=obj))

        # Action
        app.add_url_rule(PI_BASE_URL + 'action' + obj.pi_api_route, view_func=ActionView.as_view('action_' + act, action=obj), methods=obj.pi_api_methods)


if __name__ == "__main__":
    app.run(debug=DEBUG)
