"""Test the plugit proxy from an external point of view (Using the standalone proxy and a simple plugit service)"""

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
    def setup_class(self):
        self.start_process_service()
        self.start_process_proxy()
        self.session = requests.Session()

    @classmethod
    def start_process_service(self, args=[]):

        if self.process_service:
            self.process_service.kill()

        FNULL = open(os.devnull, 'w')
        self.process_service = subprocess.Popen([sys.executable, 'server.py'] + args, cwd='tests/helpers/flask_server', stdout=FNULL, stderr=FNULL)
        time.sleep(0.5)

    @classmethod
    def start_process_proxy(self, args=[]):

        if self.process_proxy:
            self.process_proxy.kill()

        FNULL = open(os.devnull, 'w')
        my_env = os.environ.copy()
        my_env['PLUGIT_SERVER'] = 'http://127.0.0.1:63441'

        self.process_proxy = subprocess.Popen([sys.executable, 'manage.py', 'runserver', '127.0.0.1:23423'] + args, cwd='examples/standalone_proxy', stdout=FNULL, stderr=FNULL, env=my_env)
        time.sleep(0.5)

    @classmethod
    def teardown_class(self):

        self.process_service.kill()
        self.process_service = None

        self.process_proxy.kill()
        self.process_proxy = None

    def do_query(self, url, method='GET', getParmeters=None, postParameters=None, files=None, headers={}):
        return self.session.request(method.upper(), 'http://127.0.0.1:23423/plugIt/' + url, params=getParmeters, data=postParameters, stream=True, headers=headers, allow_redirects=True, files=files)

    def test_homepage(self):

        retour = self.do_query('')

        assert(retour)
        assert('home_template' in retour.text)

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
