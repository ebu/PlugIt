import unittest
from nose.tools import *

import requests
import uuid
import os


class TestExternal(unittest.TestCase):
    """Class to test the plugit service"""

    p = None

    @classmethod
    def setup_class(self):
        self.start_p()

    @classmethod
    def start_p(self, args=[]):
        import subprocess
        import sys
        import time

        if self.p:
            self.p.kill()

        FNULL = open(os.devnull, 'w')
        self.p = subprocess.Popen([sys.executable, 'server.py', '63443'] + args, cwd='tests/helpers/flask_server', stdout=FNULL, stderr=FNULL)
        time.sleep(0.5)

    @classmethod
    def teardown_class(self):

        self.p.kill()
        self.p = None

    def do_query(self, url, method='GET', getParmeters=None, postParameters=None, files=None, headers={}):
        return requests.request(method.upper(), 'http://127.0.0.1:63443/' + url, params=getParmeters, data=postParameters, stream=True, headers=headers, allow_redirects=True, files=files)

    def test_ping(self):
        """Test if the server respond to the ping call"""

        data = str(uuid.uuid4())

        retour = self.do_query('ping', getParmeters={'data': data})

        assert(retour)
        assert(retour.json()['data'] == data)

    def test_version(self):
        """Test the version call"""

        retour = self.do_query('version')

        assert(retour)
        assert(retour.json()['result'] == 'Ok')
        assert(retour.json()['version'] == '1')
        assert(retour.json()['protocol'] == 'EBUio-PlugIt')

    def test_mail(self):
        """Test the mail call"""

        assert(not self.do_query('mail'))
        assert(not self.do_query('mail', 'POST'))

        retour = self.do_query('mail', 'POST', postParameters={'response_id': ''})

        assert(retour)
        assert(retour.json()['result'] != 'Ok')

        retour = self.do_query('mail', 'POST', postParameters={'response_id': '42'})

        assert(retour)
        assert(retour.json()['result'] == 'Ok')

    def test_home_template(self):
        """Test home template"""

        retour = self.do_query('template/')

        assert(retour)
        assert(retour.text.strip() == 'home_template')

    def test_home_call(self):
        """Test home call"""

        retour = self.do_query('action/')

        assert(retour)
        assert(retour.json()['home'] == '123')

    def test_home_meta(self):
        """Test home meta"""

        retour = self.do_query('meta/')

        assert(retour)
        assert(retour.json()['template_tag'] == 'c2dca2db9bb94ffbd128ee5c1644c8bb')

    def test_only_logged_user(self):
        """Test only_logged_user"""

        retour = self.do_query('meta/only_logged_user')

        assert(retour)
        assert(retour.json()['only_logged_user'])

        assert('only_logged_user' not in self.do_query('meta/').json())

    def test_only_member_user(self):
        """Test only_member_user"""

        retour = self.do_query('meta/only_member_user')

        assert(retour)
        assert(retour.json()['only_member_user'])

        assert('only_member_user' not in self.do_query('meta/').json())

    def test_only_admin_user(self):
        """Test only_admin_user"""

        retour = self.do_query('meta/only_admin_user')

        assert(retour)
        assert(retour.json()['only_admin_user'])

        assert('only_admin_user' not in self.do_query('meta/').json())

    def test_only_orga_member_user(self):
        """Test only_orga_member_user"""

        retour = self.do_query('meta/only_orga_member_user')

        assert(retour)
        assert(retour.json()['only_orga_member_user'])

        assert('only_orga_member_user' not in self.do_query('meta/').json())

    def test_only_orga_admin_user(self):
        """Test only_orga_admin_user"""

        retour = self.do_query('meta/only_orga_admin_user')

        assert(retour)
        assert(retour.json()['only_orga_admin_user'])

        assert('only_orga_admin_user' not in self.do_query('meta/').json())

    def test_cache(self):
        """Test cache"""

        retour = self.do_query('meta/cache')

        assert(retour)
        assert(retour.json()['cache_time'] == 42)
        assert(not retour.json()['cache_by_user'])

        assert('cache_time' not in self.do_query('meta/').json())

    def test_cache2(self):
        """Test cache, by user"""

        retour = self.do_query('meta/cache2')

        assert(retour)
        assert(retour.json()['cache_time'] == 48)
        assert(retour.json()['cache_by_user'])

    def test_user_info(self):
        """Test user_info"""

        retour = self.do_query('meta/user_info')

        assert(retour)
        assert(retour.json()['user_info'] == ['1', 'coucou', 3, 'thegame'])

        assert('user_info' not in self.do_query('meta/').json())

    def test_json_only(self):
        """Test json_only"""

        retour = self.do_query('meta/json_only')

        assert(retour)
        assert(retour.json()['json_only'])

        assert('json_only' not in self.do_query('meta/').json())

    def test_xml_only(self):
        """Test xml_only"""

        retour = self.do_query('meta/xml_only')

        assert(retour)
        assert(retour.json()['xml_only'])

        assert('xml_only' not in self.do_query('meta/').json())

    def test_public(self):
        """Test public"""

        retour = self.do_query('meta/public')

        assert(retour)
        assert(retour.json()['public'])

        assert('public' not in self.do_query('meta/').json())

    def test_address_in_networks(self):
        """Test address_in_networks"""

        retour = self.do_query('meta/address_in_networks')

        assert(retour)
        assert(retour.json()['address_in_networks'])

        assert('public' not in self.do_query('meta/').json())

    def test_no_template(self):
        """Test no_template"""

        retour = self.do_query('meta/no_template')

        assert(retour)
        assert(retour.json()['no_template'])

        assert('no_template' not in self.do_query('meta/').json())

    def testplugitredirect(self):
        """Test PlugItRedirect"""

        retour = self.do_query('action/plugitredirect')

        assert(retour)
        assert(retour.headers['ebuio-plugit-redirect'] == '/redire_ect')
        assert('ebuio-plugit-redirect-noprefix' not in retour.headers)
        assert('ebuio-plugit-redirect' not in self.do_query('action/').headers)

    def testplugitredirect2(self):
        """Test PlugItRedirect with no prefix"""

        retour = self.do_query('action/plugitredirect2')

        assert(retour)
        assert(retour.headers['ebuio-plugit-redirect'] == '/redire_ec2t')
        assert(retour.headers['ebuio-plugit-redirect-noprefix'] == 'True')
        assert('ebuio-plugit-redirect-noprefix' not in self.do_query('action/').headers)

    def testplugitsendfile(self):
        """Test PlugItSendFile"""

        retour = self.do_query('action/plugitsendfile')

        assert(retour)
        assert(retour.headers['ebuio-plugit-itafile'])
        assert('content-disposition' not in retour.headers)
        assert('ebuio-plugit-itafile' not in self.do_query('action/').headers)
        assert(retour.text.strip() == "This is test file 2 !")

    def testplugitsendfile2(self):
        """Test PlugItSendFile with attachement"""

        retour = self.do_query('action/plugitsendfile2')

        assert(retour)
        assert(retour.headers['ebuio-plugit-itafile'])
        assert(retour.headers['content-disposition'] == 'attachment; filename=41-file-name')
        assert('content-disposition' not in self.do_query('action/').headers)
        assert(retour.text.strip() == "This is test file 2 !")

    def testplugitsetsession(self):
        """Test PlugItSetSession"""

        retour = self.do_query('action/plugitsetsession')

        assert(retour)
        assert(retour.json()['b'] == '2')
        assert(retour.headers['ebuio-plugit-setsession-a'] == '1')
        assert('ebuio-plugit-setsession-a' not in self.do_query('action/').headers)

    def test_media(self):
        """Test media"""

        retour = self.do_query('media/testfile1')

        assert(retour)
        assert(retour.text.strip() == u"This is the text file 1")

    def test_post(self):
        """Test post requests"""

        assert(not self.do_query('action/postonly'))
        assert(self.do_query('action/postonly', 'POST', postParameters={'1': '9'}).json()['result'] == 'ok')

        assert(self.do_query('meta/postonly'))
        assert(not self.do_query('meta/postonly', 'POST'))
        assert(self.do_query('template/postonly'))
        assert(not self.do_query('template/postonly', 'POST'))

    def test_send_file(self):
        """Test file sending"""

        assert(self.do_query('action/sendfile', 'POST', files=[('testfile2', open('tests/helpers/flask_server/media/testfile2', 'r'))]).json()['result'] == 'ok')

    def test_ip(self):
        self.start_p(['ip'])

        assert(not self.do_query('ping'))

        self.start_p()

    def test_404(self):
        assert(not self.do_query('thiswontwork'))
        assert(not self.do_query('action/tralala'))
        assert(not self.do_query('template/tralala'))
        assert(not self.do_query('meta/tralala'))

    def test_etag(self):
        r = self.do_query('action/etag')

        assert(r)
        assert('ETag' in r.headers)
        assert(r.headers['ETag'] == 'this-is-an-etag')

    def test_baseurl(self):
        self.start_p(['baseurl'])

        assert(not self.do_query('ping'))
        assert(self.do_query('baseurl/ping'))

        self.start_p()
