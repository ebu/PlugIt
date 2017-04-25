"""Test internal functions and features of a service"""

import unittest
from nose.tools import *

import sys
import os
import uuid
from werkzeug.exceptions import NotFound


class _CallBack():
    def __init__(self, prop_to_set):
        for (key, value) in prop_to_set.items():
            setattr(self, key, value)


class TestBase(unittest.TestCase):
    """Common class for tests"""

    DUMMY_CONFIG_PATH = os.path.join('tests', 'dummy_config')

    @classmethod
    def setup_class(self):
        """Setup path"""
        sys.path.append(self.DUMMY_CONFIG_PATH)

    @classmethod
    def teardown_class(self):
        """Remove added value from path"""
        sys.path.remove(self.DUMMY_CONFIG_PATH)


class TestUtils(TestBase):
    """Test the utils.py file"""

    def test_decorators_action(self):
        """Test the action decorator"""
        from plugit.utils import action

        route = str(uuid.uuid4())
        template = str(uuid.uuid4())
        methods = str(uuid.uuid4())

        @action(route=route, template=template, methods=methods)
        def _tmp():
            pass

        assert(_tmp.pi_api_action)
        assert(_tmp.pi_api_route == route)
        assert(_tmp.pi_api_template == template)
        assert(_tmp.pi_api_methods == methods)

    def test_decorators_action_default(self):
        """Test the action decorator"""
        from plugit.utils import action

        @action(route='')
        def _tmp():
            pass

        assert(_tmp.pi_api_action)
        assert(_tmp.pi_api_template == '')
        assert('GET' in _tmp.pi_api_methods)
        assert(len(_tmp.pi_api_methods) == 1)

    def test_decorators_only_logger_user(self):
        """Test the only_logger_user decorator"""
        from plugit.utils import only_logged_user

        @only_logged_user()
        def _tmp():
            pass

        assert(_tmp.pi_api_only_logged_user)

    def test_decorators_only_member_user(self):
        """Test the only_member_user decorator"""
        from plugit.utils import only_member_user

        @only_member_user()
        def _tmp():
            pass

        assert(_tmp.pi_api_only_member_user)

    def test_decorators_only_admin_user(self):
        """Test the only_admin_user decorator"""
        from plugit.utils import only_admin_user

        @only_admin_user()
        def _tmp():
            pass

        assert(_tmp.pi_api_only_admin_user)

    def test_decorators_only_orga_member_user(self):
        """Test the only_orga_member_user decorator"""
        from plugit.utils import only_orga_member_user

        @only_orga_member_user()
        def _tmp():
            pass

        assert(_tmp.pi_api_only_orga_member_user)

    def test_decorators_only_orga_admin_user(self):
        """Test the only_orga_admin_user decorator"""
        from plugit.utils import only_orga_admin_user

        @only_orga_admin_user()
        def _tmp():
            pass

        assert(_tmp.pi_api_only_orga_admin_user)

    def test_decorators_cache(self):
        """Test the cache decorator"""
        from plugit.utils import cache

        time = str(uuid.uuid4())
        byUser = str(uuid.uuid4())

        @cache(time=time, byUser=byUser)
        def _tmp():
            pass

        assert(_tmp.pi_api_cache_time == time)
        assert(_tmp.pi_api_cache_by_user == byUser)

    def test_decorators_user_info(self):
        """Test the user_info decorator"""
        from plugit.utils import user_info

        props = str(uuid.uuid4())

        @user_info(props=props)
        def _tmp():
            pass

        assert(_tmp.pi_api_user_info == props)

    def test_decorators_json_only(self):
        """Test the json_only decorator"""
        from plugit.utils import json_only

        @json_only()
        def _tmp():
            pass

        assert(_tmp.pi_api_json_only)

    def test_decorators_no_template(self):
        """Test the no_template decorator"""
        from plugit.utils import no_template

        @no_template()
        def _tmp():
            pass

        assert(_tmp.pi_api_no_template)

    def test_md5checksum(self):
        """Test the md5Checksum util"""
        import tempfile
        from plugit.utils import md5Checksum

        (filehandle, filename) = tempfile.mkstemp()
        os.close(filehandle)

        file_ = open(filename, 'wb')
        file_.write('thegame\n')
        file_.close()

        assert(md5Checksum(filename) == '3a617592865c4a620d71ddf2311208c9')

        os.unlink(filename)

    def test_add_unique_postfix(self):
        """Test the add_unique_postfix function"""
        import tempfile
        from plugit.utils import add_unique_postfix

        (filehandle, filename) = tempfile.mkstemp()
        os.close(filehandle)

        assert(add_unique_postfix(filename))
        assert(filename != add_unique_postfix(filename))

        os.unlink(filename)

        # File dosen't exist: should return the same
        assert(filename == add_unique_postfix(filename))

    def test_get_session_from_request(self):
        """Test the get_session_from_request function"""
        from plugit.utils import get_session_from_request

        keya = str(uuid.uuid4())
        keyb = str(uuid.uuid4())
        valuea = str(uuid.uuid4())
        valueb = str(uuid.uuid4())
        valuec = str(uuid.uuid4())

        class R():
            headers = {
                'X-Plugitsession-' + keya: valuea,
                'X-Plugitsession-' + keyb: valueb,
                valuec: valuec,
            }

        retour = get_session_from_request(R())

        assert(keya in retour)
        assert(keyb in retour)
        assert(valuec not in retour)

        assert(retour[keya] == valuea)
        assert(retour[keyb] == valueb)

    def test_redirect(self):
        """Test PlugitRedirect"""

        from plugit.utils import PlugItRedirect

        url = str(uuid.uuid4())
        no_prefix = str(uuid.uuid4())

        _tmp = PlugItRedirect(url=url, no_prefix=no_prefix)

        assert(_tmp.no_prefix == no_prefix)
        assert(_tmp.url == url)

    def test_redirect_default(self):
        """Test PlugItRedirect with defaults values"""

        from plugit.utils import PlugItRedirect

        _tmp = PlugItRedirect(url='')

        assert(not _tmp.no_prefix)

    def test_sendfile(self):
        """Test PlugItSendFile"""

        from plugit.utils import PlugItSendFile

        mimetype = str(uuid.uuid4())
        filename = str(uuid.uuid4())
        as_attachment = str(uuid.uuid4())
        attachment_filename = str(uuid.uuid4())

        _tmp = PlugItSendFile(mimetype=mimetype, filename=filename, as_attachment=as_attachment, attachment_filename=attachment_filename)

        assert(_tmp.mimetype == mimetype)
        assert(_tmp.filename == filename)
        assert(_tmp.as_attachment == as_attachment)
        assert(_tmp.attachment_filename == attachment_filename)

    def test_sendfile_default(self):
        """Test PlugitSendFile with default values"""

        from plugit.utils import PlugItSendFile

        _tmp = PlugItSendFile(mimetype='', filename='')

        assert(not _tmp.as_attachment)
        assert(_tmp.attachment_filename == '')

    def test_setsession(self):
        """Test PlugitRedirect"""

        from plugit.utils import PlugItSetSession

        base = str(uuid.uuid4())
        things_to_set = str(uuid.uuid4())

        _tmp = PlugItSetSession(base=base, things_to_set=things_to_set)

        assert(_tmp.base == base)
        assert(_tmp.things_to_set == things_to_set)

    def test_setsession_default(self):
        """Test PlugItSetSession with defaults values"""

        from plugit.utils import PlugItSetSession

        _tmp = PlugItSetSession(base='')

        assert(_tmp.things_to_set == {})

    def test_address_in_network(self):
        from plugit.utils import addressInNetwork

        assert(addressInNetwork('123.123.123.123', '123.123.123.123/32'))
        assert(not addressInNetwork('123.123.123.123', '123.123.123.1/32'))

        assert(addressInNetwork('123.123.123.123', '123.123.123.1/24'))
        assert(not addressInNetwork('123.123.123.123', '123.123.1.1/24'))

        assert(addressInNetwork('123.123.123.123', '123.123.1.1/16'))
        assert(not addressInNetwork('123.123.123.123', '123.1.1.1/16'))

        assert(addressInNetwork('123.123.123.123', '123.1.1.1/8'))
        assert(not addressInNetwork('123.123.123.123', '1.1.1.1/8'))

        assert(addressInNetwork('123.123.123.123', '1.1.1.1/0'))
        assert(addressInNetwork('123.123.123.123', '0.0.0.0/0'))

    def test_check_ip(self):
        """Test check_ip"""

        from plugit import utils

        backup_allowed = utils.PI_ALLOWED_NETWORKS
        utils.PI_ALLOWED_NETWORKS = ['123.1.1.1/8']

        class R():
            remote_addr = '123.123.123.123'

        try:
            retour = utils.check_ip(R())
        except Exception:
            retour = False

        utils.PI_ALLOWED_NETWORKS = backup_allowed

        assert(retour)

    def test_check_ip_2(self):
        """Test check_ip"""

        from plugit import utils

        backup_allowed = utils.PI_ALLOWED_NETWORKS
        utils.PI_ALLOWED_NETWORKS = ['1.1.1.1/8']

        class R():
            remote_addr = '123.123.123.123'

        try:
            retour = utils.check_ip(R())
        except Exception:
            retour = False

        utils.PI_ALLOWED_NETWORKS = backup_allowed

        assert(not retour)


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
                os.rmdir('tests/templates')

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

        assert(json.loads(response) == "tests.service_internal.R")

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


class TestApi(TestBase):
    """Test the api.py file"""

    @classmethod
    def setup_class(self):
        super(TestApi, self).setup_class()

        self.user_key = str(uuid.uuid4())
        self.orgas_key = str(uuid.uuid4())
        self.orga_key = str(uuid.uuid4())
        self.project_members_key = str(uuid.uuid4())
        self.send_mail_key = str(uuid.uuid4())
        self.forum_key = str(uuid.uuid4())

        from plugit.api import PlugItAPI
        self.api = PlugItAPI('http://127.0.0.1:62312/')

        import subprocess
        import sys
        import time

        FNULL = open(os.devnull, 'w')
        self.p = subprocess.Popen([sys.executable, 'tests/helpers/api_server.py', self.user_key, self.orgas_key, self.orga_key, self.project_members_key, self.send_mail_key, self.forum_key], stdout=FNULL, stderr=FNULL)

        time.sleep(1)

    @classmethod
    def teardown_class(self):
        super(TestApi, self).teardown_class()

        self.p.kill()

    def test_get_user(self):
        """Test the get_user call"""

        retour = self.api.get_user(self.user_key[3])

        assert(retour)
        assert(retour.pk == self.user_key[3])
        assert(retour.id == self.user_key[3])
        assert(getattr(retour, self.user_key[::-1]) == self.user_key)

    def test_get_orgas(self):
        """Test the get_orgas call"""

        retour = self.api.get_orgas()

        assert(retour)
        assert(len(retour) == len(self.orgas_key))
        for x in self.orgas_key:
            o = retour.pop(0)
            assert(o.id == x)
            assert(o.pk == x)
            assert(getattr(o, self.orgas_key.replace(x, '')[::-1]) == self.orgas_key.replace(x, ''))

    def test_get_orga(self):
        """Test the get_orga call"""

        retour = self.api.get_orga(self.orga_key[3])

        assert(retour)
        assert(retour.pk == self.orga_key[3])
        assert(retour.id == self.orga_key[3])
        assert(getattr(retour, self.orga_key[::-1]) == self.orga_key)

    def test_get_project_members(self):
        """Test the get_project_members call"""

        retour = self.api.get_project_members()

        assert(retour)
        assert(len(retour) == len(self.project_members_key))

        for x in self.project_members_key:
            o = retour.pop(0)
            assert(o.id == x)
            assert(getattr(o, self.project_members_key.replace(x, '')[::-1]) == self.project_members_key.replace(x, ''))

    def test_send_mail(self):
        """Test the send mail call"""

        retour = self.api.send_mail(self.send_mail_key[1], self.send_mail_key[5], [self.send_mail_key[0], self.send_mail_key[4]], self.send_mail_key[9])

        assert(retour)
        assert(retour.text == self.send_mail_key)

    def test_send_mail_2(self):
        """Test the send mail call, with a response_id"""

        retour = self.api.send_mail(self.send_mail_key[1], self.send_mail_key[5], [self.send_mail_key[0], self.send_mail_key[4]], self.send_mail_key[9], self.send_mail_key[7])

        assert(retour)
        assert(retour.text == self.send_mail_key[::-1])

    def test_ebuio_forum(self):
        """Test the ebuio_forum call"""
        retour = self.api.ebuio_forum(self.forum_key[2], self.forum_key[6], self.forum_key[10])

        assert(retour)
        assert(retour['key'] == self.forum_key)

    def test_ebuio_forum_tags(self):
        """Test the ebuio_forum_tags call"""
        retour = self.api.ebuio_forum(self.forum_key[2], self.forum_key[6], self.forum_key[10], self.forum_key[8])

        assert(retour)
        assert(retour['key'] == self.forum_key[::-1])
