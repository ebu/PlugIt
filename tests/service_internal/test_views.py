from _utils import TestBase, _CallBack


from nose.tools import *


import uuid
from werkzeug.exceptions import NotFound


class TestViews(TestBase):
    """Test views.py"""

    def patch_view(self, ip='127.0.0.1', dont_jsonify=False):
        """Patch the plugit view with special callbacks"""

        from plugit import views
        import json

        self.plugitviews = views

        self.bkp_request = self.plugitviews.request
        self.bkp_md5 = self.plugitviews.md5Checksum
        self.bkp_response = self.plugitviews.make_response
        self.bkp_jsonfy = self.plugitviews.jsonify

        class R():
            remote_addr = ip
            headers = {}

        def false_md5_checksum(value):
            return value * 2

        def false_make_response(obj):
            class Rep():
                retour = obj
                headers = {}
            return Rep()

        def false_jsonfy(obj):
            if dont_jsonify:
                return obj
            return json.dumps(obj)

        self.plugitviews.request = R()
        self.plugitviews.md5Checksum = false_md5_checksum
        self.plugitviews.make_response = false_make_response
        self.plugitviews.jsonify = false_jsonfy

    def unpatch_view(self):
        """Revert changes done to the view"""

        self.plugitviews.request = self.bkp_request
        self.plugitviews.md5Checksum = self.bkp_md5
        self.plugitviews.make_response = self.bkp_response
        self.plugitviews.jsonify = self.bkp_jsonfy

    def test_meta(self):
        """Test the MetaView"""

        import json
        import datetime

        self.patch_view()

        pi_api_template = str(uuid.uuid4())
        pi_api_only_logged_user = str(uuid.uuid4())
        pi_api_only_member_user = str(uuid.uuid4())
        pi_api_only_admin_user = str(uuid.uuid4())
        pi_api_only_orga_member_user = str(uuid.uuid4())
        pi_api_only_orga_admin_user = str(uuid.uuid4())
        pi_api_cache_time = str(uuid.uuid4())
        pi_api_cache_by_user = str(uuid.uuid4())
        pi_api_user_info = str(uuid.uuid4())
        pi_api_json_only = str(uuid.uuid4())
        pi_api_xml_only = str(uuid.uuid4())
        pi_api_public = str(uuid.uuid4())
        pi_api_address_in_networks = str(uuid.uuid4())
        pi_api_no_template = str(uuid.uuid4())

        props = {
            'pi_api_template': pi_api_template,
            'pi_api_only_logged_user': pi_api_only_logged_user,
            'pi_api_only_member_user': pi_api_only_member_user,
            'pi_api_only_admin_user': pi_api_only_admin_user,
            'pi_api_only_orga_member_user': pi_api_only_orga_member_user,
            'pi_api_only_orga_admin_user': pi_api_only_orga_admin_user,
            'pi_api_cache_time': pi_api_cache_time,
            'pi_api_cache_by_user': pi_api_cache_by_user,
            'pi_api_user_info': pi_api_user_info,
            'pi_api_json_only': pi_api_json_only,
            'pi_api_public': pi_api_public,
            'pi_api_xml_only': pi_api_xml_only,
            'pi_api_address_in_networks': pi_api_address_in_networks,
            'pi_api_no_template': pi_api_no_template
        }

        mv = self.plugitviews.MetaView(_CallBack(props))

        response = mv.dispatch_request()

        self.unpatch_view()

        data = json.loads(response.retour)

        assert(data['template_tag'] == (('templates/' + pi_api_template) * 2))
        assert(data['only_logged_user'] == pi_api_only_logged_user)
        assert(data['only_member_user'] == pi_api_only_member_user)
        assert(data['only_admin_user'] == pi_api_only_admin_user)
        assert(data['only_orga_member_user'] == pi_api_only_orga_member_user)
        assert(data['only_orga_admin_user'] == pi_api_only_orga_admin_user)
        assert(data['cache_time'] == pi_api_cache_time)
        assert(data['cache_by_user'] == pi_api_cache_by_user)
        assert(data['user_info'] == pi_api_user_info)
        assert(data['json_only'] == pi_api_json_only)
        assert(data['xml_only'] == pi_api_xml_only)
        assert(data['public'] == pi_api_public)
        assert(data['address_in_networks'] == pi_api_address_in_networks)
        assert(data['no_template'] == pi_api_no_template)

        assert(response.headers['Cache-Control'] == 'public, max-age=' + str(self.plugitviews.PI_META_CACHE))
        date = datetime.datetime.strptime(response.headers['Expire'], "%a, %d %b %Y %H:%M:%S GMT")

        assert(date)

        now = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.plugitviews.PI_META_CACHE)
        now = now - datetime.timedelta(microseconds=now.microsecond)

        # If we just switched seconds. No reason we got more than this of runtime...
        assert(date == now or data == (now - datetime.timedelta(seconds=1)))

    def test_meta_ip(self):
        """Check if the meta view check the IP"""

        from plugit import utils

        backup_allowed = utils.PI_ALLOWED_NETWORKS
        utils.PI_ALLOWED_NETWORKS = ['127.0.0.0/8']

        self.patch_view('1.2.3.4')

        mv = self.plugitviews.MetaView({})

        try:
            mv.dispatch_request()
        except NotFound:
            self.unpatch_view()
            utils.PI_ALLOWED_NETWORKS = backup_allowed
            return  # Ok :)

        self.unpatch_view()
        utils.PI_ALLOWED_NETWORKS = backup_allowed

        assert(False)

    def test_template(self):
        """Test the template view"""

        self.patch_view()

        file_content = '\n'.join([str(uuid.uuid4()) for x in range(0, 0xF)])

        import tempfile
        import os

        if not os.path.isdir('tests/service_internal/templates'):
            delete_the_template_folder = True
            os.mkdir('tests/service_internal/templates')
        else:
            delete_the_template_folder = False

        (handle, tmp_template) = tempfile.mkstemp(dir='tests/service_internal/templates/')
        handle = open(tmp_template, 'wb')
        handle.write(file_content)
        handle.close()
        current_dir = os.getcwd()

        try:
            mv = self.plugitviews.TemplateView(_CallBack({'pi_api_template': tmp_template.split(os.sep)[-1]}))

            from flask import Flask
            app = Flask(__name__)
            with app.app_context():
                with app.test_request_context():
                    os.chdir(os.sep.join(tmp_template.split(os.sep)[:-2]))
                    response = mv.dispatch_request()
                    os.chdir(current_dir)

            self.unpatch_view()
        finally:
            os.chdir(current_dir)
            os.unlink(tmp_template)

            if delete_the_template_folder:
                os.rmdir('tests/service_internal/templates')

        response.direct_passthrough = False

        assert(response.data == file_content)

    def test_template_ip(self):
        """Check if the template view check the IP"""

        from plugit import utils

        backup_allowed = utils.PI_ALLOWED_NETWORKS
        utils.PI_ALLOWED_NETWORKS = ['127.0.0.0/8']

        self.patch_view('1.2.3.4')

        mv = self.plugitviews.TemplateView({})

        try:
            mv.dispatch_request()
        except NotFound:
            self.unpatch_view()
            utils.PI_ALLOWED_NETWORKS = backup_allowed
            return  # Ok :)

        self.unpatch_view()
        utils.PI_ALLOWED_NETWORKS = backup_allowed

        assert(False)

    def test_action(self):
        """Test action"""

        import json

        self.patch_view()

        data = {'1': str(uuid.uuid4()), '2': str(uuid.uuid4())}

        def _tmpa(__):
            return data

        mv = self.plugitviews.ActionView(_tmpa)
        response = mv.dispatch_request()
        self.unpatch_view()

        assert(json.loads(response) == data)

    def test_action_got_extra_parameters(self):
        """Test action"""

        import json

        self.patch_view()

        data = {'1': str(uuid.uuid4()), '2': str(uuid.uuid4())}

        def _tmpa(__, extra_data):
            return extra_data

        mv = self.plugitviews.ActionView(_tmpa)
        response = mv.dispatch_request(data)
        self.unpatch_view()

        assert(json.loads(response) == data)

    def test_action_got_request(self):
        """Test action"""

        import json

        self.patch_view()

        def _tmpa(request):
            return request.__class__.__module__ + '.' + request.__class__.__name__

        mv = self.plugitviews.ActionView(_tmpa)
        from flask import Flask
        app = Flask(__name__)
        with app.app_context():
            with app.test_request_context():
                response = mv.dispatch_request()
        self.unpatch_view()

        assert(json.loads(response) == "tests.service_internal.test_views.R")

    def test_action_set_session(self):

        self.patch_view(dont_jsonify=True)

        data = {'a': str(uuid.uuid4()), 'b': str(uuid.uuid4()), 'headers': {}}
        session_key = str(uuid.uuid4())
        session_value = str(uuid.uuid4())

        def _tmpa(__):
            from plugit.utils import PlugItSetSession
            return PlugItSetSession(_CallBack(data), {session_key: session_value})

        mv = self.plugitviews.ActionView(_tmpa)
        response = mv.dispatch_request()
        self.unpatch_view()

        assert(response.a == data['a'])
        assert(response.b == data['b'])
        assert(response.headers['EbuIo-PlugIt-SetSession-' + session_key] == session_value)

    def test_action_redirect(self):

        self.patch_view(dont_jsonify=True)

        redirect_dest = str(uuid.uuid4())

        def _tmpa(__):
            from plugit.utils import PlugItRedirect
            return PlugItRedirect(redirect_dest, no_prefix=False)

        mv = self.plugitviews.ActionView(_tmpa)
        response = mv.dispatch_request()
        self.unpatch_view()

        assert(response.headers['EbuIo-PlugIt-Redirect'] == redirect_dest)
        assert('EbuIo-PlugIt-Redirect-NoPrefix' not in response.headers)

    def test_action_redirect_no_prefix(self):

        self.patch_view(dont_jsonify=True)

        redirect_dest = str(uuid.uuid4())

        def _tmpa(__):
            from plugit.utils import PlugItRedirect
            return PlugItRedirect(redirect_dest, no_prefix=True)

        mv = self.plugitviews.ActionView(_tmpa)
        response = mv.dispatch_request()
        self.unpatch_view()

        assert(response.headers['EbuIo-PlugIt-Redirect'] == redirect_dest)
        assert(response.headers['EbuIo-PlugIt-Redirect-NoPrefix'] == 'True')

    def test_action_send_file(self):
        """Test the action view sending a file"""

        self.patch_view(dont_jsonify=True)

        file_content = '\n'.join([str(uuid.uuid4()) for x in range(0, 0xF)])

        minetype = str(uuid.uuid4())

        import tempfile
        import os

        if not os.path.isdir('tests/templates'):
            delete_the_template_folder = True
            os.mkdir('tests/templates')
        else:
            delete_the_template_folder = False

        (handle, tmp_template) = tempfile.mkstemp(dir='tests/templates/')
        handle = open(tmp_template, 'wb')
        handle.write(file_content)
        handle.close()
        current_dir = os.getcwd()

        def _tmpa(__):
            from plugit.utils import PlugItSendFile
            return PlugItSendFile(tmp_template, minetype)

        try:
            mv = self.plugitviews.ActionView(_tmpa)

            from flask import Flask
            app = Flask(__name__)
            with app.app_context():
                with app.test_request_context():
                    os.chdir(os.sep.join(tmp_template.split(os.sep)[:-2]))
                    response = mv.dispatch_request()
                    os.chdir(current_dir)

            self.unpatch_view()
        finally:
            os.chdir(current_dir)
            os.unlink(tmp_template)

            if delete_the_template_folder:
                os.rmdir('tests/templates')

        response.direct_passthrough = False

        assert(response.data == file_content)
        assert(response.headers['Content-Type'] == minetype)

    def test_action_send_file_2(self):
        """Test the action view sending a file"""

        self.patch_view(dont_jsonify=True)

        file_content = '\n'.join([str(uuid.uuid4()) for x in range(0, 0xF)])

        minetype = str(uuid.uuid4())
        atta_filename = str(uuid.uuid4())

        import tempfile
        import os

        if not os.path.isdir('tests/templates'):
            delete_the_template_folder = True
            os.mkdir('tests/templates')
        else:
            delete_the_template_folder = False

        (handle, tmp_template) = tempfile.mkstemp(dir='tests/templates/')
        handle = open(tmp_template, 'wb')
        handle.write(file_content)
        handle.close()
        current_dir = os.getcwd()

        def _tmpa(__):
            from plugit.utils import PlugItSendFile
            return PlugItSendFile(tmp_template, minetype, as_attachment=True, attachment_filename=atta_filename)

        try:
            mv = self.plugitviews.ActionView(_tmpa)

            from flask import Flask
            app = Flask(__name__)
            with app.app_context():
                with app.test_request_context():
                    os.chdir(os.sep.join(tmp_template.split(os.sep)[:-2]))
                    response = mv.dispatch_request()
                    os.chdir(current_dir)

            self.unpatch_view()
        finally:
            os.chdir(current_dir)
            os.unlink(tmp_template)

            if delete_the_template_folder:
                os.rmdir('tests/templates')

        response.direct_passthrough = False

        assert(response.data == file_content)
        assert(response.headers['Content-Type'] == minetype)
        assert(response.headers['Content-Disposition'] == "attachment; filename=" + atta_filename)
