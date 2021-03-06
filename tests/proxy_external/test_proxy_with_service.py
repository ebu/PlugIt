import unittest
from nose.tools import *

import requests
import uuid
import os
import time
import subprocess
import sys


class TestExternal(unittest.TestCase):
    """Class to test the plugit proxy, with a running service"""

    process_service = None
    process_proxy = None
    session = None

    @classmethod
    def setup_class(cls):
        cls.start_process_service()
        cls.start_process_proxy()
        cls.session = requests.Session()

    @classmethod
    def start_process_service(cls, args=[]):

        if cls.process_service:
            cls.process_service.kill()

        FNULL = open(os.devnull, 'w')
        cls.process_service = subprocess.Popen([sys.executable, 'server.py', '63442'] + args, cwd='tests/helpers/flask_server', stdout=FNULL, stderr=FNULL)

        for x in range(50):
            try:
                requests.get('http://127.0.0.1:63442')
                return
            except:
                time.sleep(0.1)

    @classmethod
    def start_process_proxy(cls, args=[]):

        if cls.process_proxy:
            cls.process_proxy.kill()

        FNULL = open(os.devnull, 'w')
        my_env = os.environ.copy()
        my_env['PLUGIT_SERVER'] = 'http://127.0.0.1:63442'

        cls.process_proxy = subprocess.Popen([sys.executable, 'manage.py', 'runserver', '127.0.0.1:23423'] + args, cwd='examples/standalone_proxy', env=my_env, stdout=FNULL, stderr=FNULL)

        for x in range(50):
            try:
                requests.get('http://127.0.0.1:23423')
                return
            except:
                time.sleep(0.1)

    @classmethod
    def teardown_class(cls):

        cls.process_service.kill()
        cls.process_service = None

        cls.process_proxy.kill()
        cls.process_proxy = None

    def do_query(self, url, method='GET', getParmeters=None, postParameters=None, files=None, headers={}):
        return self.session.request(method.upper(), 'http://127.0.0.1:23423/plugIt/' + url, params=getParmeters, data=postParameters, stream=True, headers=headers, allow_redirects=True, files=files)

    def test_homepage(self):

        retour = self.do_query('')

        assert(retour)
        assert('home_template' in retour.text)

    def test_remote_addr_header(self):

        retour = self.do_query('remote_addr')

        assert(retour)
        assert('127.0.0.1' in retour.text)

    def test_only_logged_user_ano(self):
        self.do_query('ebuio_setUser?mode=ano')

        retour = self.do_query('only_logged_user')

        assert(not retour)
        assert(retour.status_code == 403)
        assert('home_template' not in retour.text)

    def test_only_logged_user_log(self):
        self.do_query('ebuio_setUser?mode=log')

        retour = self.do_query('only_logged_user')

        assert(retour)
        assert('home_template' in retour.text)

    def test_only_logged_user_mem(self):
        self.do_query('ebuio_setUser?mode=mem')

        retour = self.do_query('only_logged_user')

        assert(retour)
        assert('home_template' in retour.text)

    def test_only_logged_user_adm(self):
        self.do_query('ebuio_setUser?mode=adm')

        retour = self.do_query('only_logged_user')

        assert(retour)
        assert('home_template' in retour.text)

    def test_only_member_user_ano(self):
        self.do_query('ebuio_setUser?mode=ano')

        retour = self.do_query('only_member_user')

        assert(not retour)
        assert(retour.status_code == 403)
        assert('home_template' not in retour.text)

    def test_only_member_user_log(self):
        self.do_query('ebuio_setUser?mode=log')

        retour = self.do_query('only_member_user')

        assert(not retour)
        assert(retour.status_code == 403)
        assert('home_template' not in retour.text)

    def test_only_member_user_mem(self):
        self.do_query('ebuio_setUser?mode=mem')

        retour = self.do_query('only_member_user')

        assert(retour)
        assert('home_template' in retour.text)

    def test_only_member_user_adm(self):
        self.do_query('ebuio_setUser?mode=adm')

        retour = self.do_query('only_member_user')

        assert(retour)
        assert('home_template' in retour.text)

    def test_only_admin_user_ano(self):
        self.do_query('ebuio_setUser?mode=ano')

        retour = self.do_query('only_admin_user')

        assert(not retour)
        assert(retour.status_code == 403)
        assert('home_template' not in retour.text)

    def test_only_admin_user_log(self):
        self.do_query('ebuio_setUser?mode=log')

        retour = self.do_query('only_admin_user')

        assert(not retour)
        assert(retour.status_code == 403)
        assert('home_template' not in retour.text)

    def test_only_admin_user_mem(self):
        self.do_query('ebuio_setUser?mode=mem')

        retour = self.do_query('only_admin_user')

        assert(not retour)
        assert(retour.status_code == 403)
        assert('home_template' not in retour.text)

    def test_only_admin_user_adm(self):
        self.do_query('ebuio_setUser?mode=adm')

        retour = self.do_query('only_admin_user')

        assert(retour)
        assert('home_template' in retour.text)

    def test_only_orga_member_user_ano(self):
        self.do_query('ebuio_setUser?mode=ano')

        retour = self.do_query('only_orga_member_user')

        assert(not retour)
        assert(retour.status_code == 403)
        assert('home_template' not in retour.text)

    def test_only_orga_member_user_log(self):
        self.do_query('ebuio_setUser?mode=log')

        retour = self.do_query('only_orga_member_user')

        assert(not retour)
        assert(retour.status_code == 403)
        assert('home_template' not in retour.text)

    def test_only_orga_member_user_mem(self):
        self.do_query('ebuio_setUser?mode=mem')

        retour = self.do_query('only_orga_member_user')

        assert(retour)
        assert('home_template' in retour.text)

    def test_only_orga_member_user_adm(self):
        self.do_query('ebuio_setUser?mode=adm')

        retour = self.do_query('only_orga_member_user')

        assert(retour)
        assert('home_template' in retour.text)

    def test_only_orga_admin_user_ano(self):
        self.do_query('ebuio_setUser?mode=ano')

        retour = self.do_query('only_orga_admin_user')

        assert(not retour)
        assert(retour.status_code == 403)
        assert('home_template' not in retour.text)

    def test_only_orga_admin_user_log(self):
        self.do_query('ebuio_setUser?mode=log')

        retour = self.do_query('only_orga_admin_user')

        assert(not retour)
        assert(retour.status_code == 403)
        assert('home_template' not in retour.text)

    def test_only_orga_admin_user_mem(self):
        self.do_query('ebuio_setUser?mode=mem')

        retour = self.do_query('only_orga_admin_user')

        assert(not retour)
        assert(retour.status_code == 403)
        assert('home_template' not in retour.text)

    def test_only_orga_admin_user_adm(self):
        self.do_query('ebuio_setUser?mode=adm')

        retour = self.do_query('only_orga_admin_user')

        assert(retour)
        assert('home_template' in retour.text)

    def test_cache_1(self):

        retour = self.do_query('cacheTime')
        assert(retour)
        time.sleep(1)

        retour2 = self.do_query('cacheTime')
        assert(retour2)

        assert(retour.text == retour2.text)

    def test_cache_2(self):

        self.do_query('ebuio_setUser?mode=ano')

        retour = self.do_query('cacheTime2')
        assert(retour)
        time.sleep(1)

        self.do_query('ebuio_setUser?mode=adm')
        retour2 = self.do_query('cacheTime2')
        assert(retour2)

        assert(retour.text != retour2.text)

    def test_user_parameters(self):

        self.do_query('ebuio_setUser?mode=ano')

        retour = self.do_query('user_pk')
        assert(retour)

        self.do_query('ebuio_setUser?mode=adm')
        retour2 = self.do_query('user_pk')
        assert(retour2)

        assert(retour.text != retour2.text)

    def test_500(self):
        retour = self.do_query('generate_500')
        assert(not retour)
        assert(retour.status_code == 500)

    def test_json_only(self):
        retour = self.do_query('json_only')
        assert(retour)
        assert(retour.text == "{}")
        assert('json' not in retour.headers['content-type'])

    def test_xml_only(self):
        retour = self.do_query('xml_only')
        assert(retour)
        assert(retour.text == "<a></a>")
        assert('xml' in retour.headers['content-type'])

    def test_addr_in_network_ok(self):
        assert(self.do_query('address_in_networks'))

    def test_addr_in_network_not_ok(self):
        assert(not self.do_query('address_in_networks_outside'))

    def test_json_headers(self):
        retour = self.do_query('json_only', headers={'Accept': 'text/json'})
        assert(retour)
        assert(retour.text == "{}")
        assert('json' in retour.headers['content-type'])

    def test_no_template(self):
        retour = self.do_query('no_template')
        assert(retour)
        assert(retour.text.strip() == "home_template")

    def test_redirect(self):
        retour = self.do_query('external_plugitredirect')
        assert(retour)
        assert('redirected' in retour.text)

    def test_redirect2(self):
        retour = self.do_query('external_plugitredirect2')
        assert(retour)
        assert('redirected' in retour.text)

    def test_send_file(self):
        retour = self.do_query('plugitsendfile')
        assert(retour)
        assert('This is test file 2 !' in retour.text)
        assert('41-file-name' not in retour.headers['content-disposition'])
        assert('123-mine-type' in retour.headers['content-type'])

    def test_send_file_2(self):
        retour = self.do_query('plugitsendfile2')
        assert(retour)
        assert('This is test file 2 !' in retour.text)
        assert('41-file-name' in retour.headers['content-disposition'])
        assert('123-mine-type' in retour.headers['content-type'])

    def test_session(self):

        retour = self.do_query('plugitsetsession_set_time')
        assert(retour)

        retour2 = self.do_query('plugitsetsession_get_time')
        assert(retour2)

        assert(retour.text == retour2.text)

    def test_token(self):

        retour = self.do_query('csrf_token')
        assert(retour)
        assert(retour.text)
        assert('csrftoken' in retour.cookies)

    def test_post_only(self):

        assert(not self.do_query('postonly'))

        csrf_token = self.do_query('csrf_token')
        assert(not self.do_query('postonly', 'POST', headers={'X-CSRFToken': csrf_token.cookies['csrftoken']}))

        csrf_token = self.do_query('csrf_token')
        retour = self.do_query('postonly', 'POST', None, {'1': '9'}, headers={'X-CSRFToken': csrf_token.cookies['csrftoken']})
        assert(retour)
        assert('home_template' in retour.text)

    def test_sendfile(self):

        csrf_token = self.do_query('csrf_token')
        retour = self.do_query('sendfile_external', 'POST', files={'testfile1': open('tests/helpers/flask_server/media/testfile1', 'rb')}, headers={'X-CSRFToken': csrf_token.cookies['csrftoken']})
        assert(not retour)

        csrf_token = self.do_query('csrf_token')
        retour = self.do_query('sendfile_external', 'POST', files={'testfile2': open('tests/helpers/flask_server/media/testfile1', 'rb')}, headers={'X-CSRFToken': csrf_token.cookies['csrftoken']})
        assert(retour)
        assert('err' in retour.text)

        csrf_token = self.do_query('csrf_token')
        retour = self.do_query('sendfile_external', 'POST', files={'testfile2': open('tests/helpers/flask_server/media/testfile2', 'rb')}, headers={'X-CSRFToken': csrf_token.cookies['csrftoken']})
        assert(retour)
        assert('ok' in retour.text)

    def test_generate_special_code_429(self):
        retour = self.do_query('generate_429')
        assert(retour.status_code == 429)

    def test_generate_special_code_404(self):
        retour = self.do_query('generate_404')
        assert(retour.status_code == 404)

    def test_generate_special_code_403(self):
        retour = self.do_query('generate_403')
        assert(retour.status_code == 403)

    def test_generate_special_code_401(self):
        retour = self.do_query('generate_401')
        assert(retour.status_code == 401)

    def test_generate_special_code_304(self):
        retour = self.do_query('generate_304')
        assert(retour.status_code == 304)

    def test_send_etag(self):
        retour = self.do_query('etag')
        assert(retour.status_code == 200)
        assert('ETag' in retour.headers)
        assert(retour.headers['ETag'] == 'this-is-an-etag')

    def test_if_none_match(self):

        k = str(uuid.uuid4())

        retour = self.do_query('if_none_match', headers={'If-None-Match': k})

        assert(retour)
        assert(k in retour.text)

    def test_cross_domain(self):

        k = str(uuid.uuid4())

        retour = self.do_query('crossdomain', headers={'Origin': k})

        assert(retour)
        assert('Access-Control-Allow-Origin' in retour.headers)
        assert(retour.headers['Access-Control-Allow-Origin'] == 'test')
        assert(k in retour.text)

    def test_cross_domain_options(self):

        k = str(uuid.uuid4())

        retour = self.do_query('crossdomain', 'OPTIONS', headers={'Origin': k})

        assert(retour)
        assert('Access-Control-Allow-Origin' in retour.headers)
        assert(retour.headers['Access-Control-Allow-Origin'] == 'test')
        assert(k not in retour.text)
