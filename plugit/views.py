from flask import jsonify, request, make_response, send_from_directory, send_file
from flask.views import View
from datetime import datetime, timedelta

from utils import check_ip, md5Checksum, PlugItRedirect, PlugItSendFile, PlugItSetSession

from params import PI_META_CACHE


class MetaView(View):
    """The dynamic view (based on the current action) for the /meta method"""

    def __init__(self, action):
        self.action = action

    def dispatch_request(self, *args, **kwargs):

        check_ip(request)

        objResponse = {}

        # Template information
        objResponse['template_tag'] = ("" if self.action.pi_api_template == "" else
                                       md5Checksum('templates/' + self.action.pi_api_template))

        for attribute in (u'only_logged_user', u'only_member_user', u'only_admin_user',
                          u'only_orga_member_user', u'only_orga_admin_user',  # User restrictions
                          u'cache_time', u'cache_by_user',  # Cache information
                          u'user_info', u'public', u'json_only', u'xml_only',
                          u'no_template', u'address_in_networks'):  # Requested user infos + JSON-only
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

        check_ip(request)

        # We just return the content of the template
        return send_from_directory('templates/', self.action.pi_api_template)


class ActionView(View):
    """The dynamic view (based on the current action) for the /action method"""

    def __init__(self, action):
        self.action = action

    @classmethod
    def as_view_custom(cls, *args, **kwargs):
        r = ActionView.as_view(*args, **kwargs)

        if hasattr(kwargs['action'], 'pi_api_crossdomain'):
            r.provide_automatic_options = False
        return r

    def dispatch_request(self, *args, **kwargs):

        check_ip(request)

        # Call the action
        if getattr(request, 'method', 'GET') != 'OPTIONS':
            result = self.action(request, *args, **kwargs)
        else:
            result = {}

        headers = {}

        if isinstance(result, PlugItSetSession):
            headers = result.things_to_set
            result = result.base

        def update_headers():
            for (key, value) in headers.items():
                response.headers['EbuIo-PlugIt-SetSession-' + key] = value

            if hasattr(self.action, 'pi_api_send_etag'):
                if result:
                    etag = result.pop('_plugit_etag', None)
                    if etag:
                        response.headers['ETag'] = etag

            if hasattr(self.action, 'pi_api_crossdomain'):

                response.headers['Access-Control-Allow-Origin'] = self.action.pi_api_crossdomain_data['origin']

                if self.action.pi_api_crossdomain_data['methods']:
                    response.headers['Access-Control-Allow-Methods'] = self.action.pi_api_crossdomain_data['methods']

                response.headers['Access-Control-Max-Age'] = self.action.pi_api_crossdomain_data['max_age']

                if self.action.pi_api_crossdomain_data['headers']:
                    response.headers['Access-Control-Allow-Headers'] = self.action.pi_api_crossdomain_data['headers']

        # Is it a redirect ?
        if isinstance(result, PlugItRedirect):
            response = make_response("")
            response.headers['EbuIo-PlugIt-Redirect'] = result.url
            if result.no_prefix:
                response.headers['EbuIo-PlugIt-Redirect-NoPrefix'] = 'True'
            update_headers()

            return response
        elif isinstance(result, PlugItSendFile):
            response = send_file(result.filename, mimetype=result.mimetype, as_attachment=result.as_attachment, attachment_filename=result.attachment_filename)
            response.headers['EbuIo-PlugIt-ItAFile'] = 'True'
            update_headers()

            return response

        response = jsonify(result)

        update_headers()

        return response
