from _utils import TestBase


from nose.tools import *


import os
import uuid


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

    def test_decorators_address_in_networks(self):
        """Test the address_in_networks decorator"""
        from plugit.utils import address_in_networks

        networks = [str(uuid.uuid4())]

        @address_in_networks(networks)
        def _tmp():
            pass

        assert(_tmp.pi_api_address_in_networks == networks)

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

    def test_decorators_xml_only(self):
        """Test the xml_only decorator"""
        from plugit.utils import xml_only

        @xml_only()
        def _tmp():
            pass

        assert(_tmp.pi_api_xml_only)

    def test_decorators_public(self):
        """Test the public decorator"""
        from plugit.utils import public

        @public()
        def _tmp():
            pass

        assert(_tmp.pi_api_public)

    def test_decorators_no_template(self):
        """Test the no_template decorator"""
        from plugit.utils import no_template

        @no_template()
        def _tmp():
            pass

        assert(_tmp.pi_api_no_template)

    def test_decorators_send_etag(self):
        """Test the send_etag decorator"""
        from plugit.utils import send_etag

        @send_etag()
        def _tmp():
            pass

        assert(_tmp.pi_api_send_etag)

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

    def test_check_ip_proxy(self):
        """Test check_ip with proxy mode"""

        from plugit import utils

        backup_allowed = utils.PI_ALLOWED_NETWORKS

        class R():
            remote_addr = '11.11.11.11'
            access_route = ['22.22.22.22']

        utils.PI_ALLOWED_NETWORKS = ['11.11.11.11/32']
        try:
            retour_no_proxy_no_proxy = utils.check_ip(R())
        except Exception:
            retour_no_proxy_no_proxy = False

        utils.PI_ALLOWED_NETWORKS = ['22.22.22.22/32']
        try:
            retour_no_proxy_proxy = utils.check_ip(R())
        except Exception:
            retour_no_proxy_proxy = False

        utils.PI_ALLOWED_NETWORKS = ['11.11.11.11/32']
        utils.PI_USE_PROXY_IP = True
        try:
            retour_proxy_no_proxy = utils.check_ip(R())
        except Exception:
            retour_proxy_no_proxy = False

        utils.PI_ALLOWED_NETWORKS = ['22.22.22.22/32']
        try:
            retour_proxy_proxy = utils.check_ip(R())
        except Exception:
            retour_proxy_proxy = False

        utils.PI_ALLOWED_NETWORKS = backup_allowed
        utils.PI_USE_PROXY_IP = False

        assert(retour_no_proxy_no_proxy)
        assert(retour_proxy_proxy)
        assert(not retour_no_proxy_proxy)
        assert(not retour_proxy_no_proxy)
