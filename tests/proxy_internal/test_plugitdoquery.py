from _utils import TestBase


import os
import sys
import uuid
import subprocess
import time
import tempfile
import requests


class TestPlugItDoQueryTest(TestBase):

    @classmethod
    def setup_class(cls):
        super(TestPlugItDoQueryTest, cls).setup_class()
        FNULL = open(os.devnull, 'w')
        cls.p = subprocess.Popen([sys.executable, 'doquery_server.py'], cwd='tests/helpers', stdout=FNULL, stderr=FNULL)

        from plugit_proxy.plugIt import PlugIt
        cls.plugit = PlugIt("http://127.0.0.1:62314")

        for x in range(50):
            try:
                requests.get('http://127.0.0.1:62314')
                return
            except:
                time.sleep(0.1)

    @classmethod
    def teardown_class(cls):
        super(TestPlugItDoQueryTest, cls).teardown_class()
        cls.p.kill()

    def test_get(self):
        retour = self.plugit.doQuery("test_get").json()
        assert(retour['method'] == 'GET')

    def test_404(self):
        retour = self.plugit.doQuery("/_")
        assert(not retour)

    def test_get_param(self):
        p = str(uuid.uuid4())
        retour = self.plugit.doQuery("test_get", getParmeters={'get_param': p}).json()
        assert(retour['method'] == 'GET')
        assert(retour['get_param'] == p)

    def test_post(self):
        retour = self.plugit.doQuery("test_post", method='POST').json()
        assert(retour['method'] == 'POST')

    def test_post_param(self):
        p = str(uuid.uuid4())
        retour = self.plugit.doQuery("test_post", method='POST', postParameters={'post_param': p}).json()
        assert(retour['method'] == 'POST')
        assert(retour['post_param'] == p)

    def test_post_param_list(self):
        p = [str(uuid.uuid4()), str(uuid.uuid4())]
        retour = self.plugit.doQuery("test_post_list", method='POST', postParameters={'post_param': p}).json()
        assert(retour['method'] == 'POST')
        assert(retour['post_param'] == p)

    def test_post_getparam(self):
        p = str(uuid.uuid4())
        retour = self.plugit.doQuery("test_post", method='POST', getParmeters={'get_param': p}).json()
        assert(retour['method'] == 'POST')
        assert(retour['get_param'] == p)

    def test_extraHeaders_get(self):
        p = str(uuid.uuid4())

        retour = self.plugit.doQuery("test_extraHeaders", method='GET', extraHeaders={'test': p}).json()
        assert(retour['x-plugit-test'] == p)

    def test_extraHeaders_post(self):
        p = str(uuid.uuid4())

        retour = self.plugit.doQuery("test_extraHeaders", method='POST', extraHeaders={'test': p}).json()
        assert(retour['x-plugit-test'] == p)

    def test_extraHeaders_bytes_get(self):
        p = str(uuid.uuid4()).encode('utf-8')

        retour = self.plugit.doQuery("test_extraHeaders", method='GET', extraHeaders={'test': p}).json()
        assert(retour['x-plugit-test'] == str(p))

    def test_session_get(self):
        p = str(uuid.uuid4())

        retour = self.plugit.doQuery("test_session", method='GET', session={'test': p}).json()
        assert(retour['x-plugitsession-test'] == p)
        assert(retour['cookie-test'] == p)

    def test_session_post(self):
        p = str(uuid.uuid4())

        retour = self.plugit.doQuery("test_session", method='POST', session={'test': p}).json()
        assert(retour['x-plugitsession-test'] == p)
        assert(retour['cookie-test'] == p)

    def test_fileupload(self):

        p = str(uuid.uuid4())
        (handle, tmpfile) = tempfile.mkstemp()
        handle = open(tmpfile, 'wb')
        handle.write(p)
        handle.close()

        class FileObj():
            def temporary_file_path(self):
                return tmpfile
            name = 'test'

        retour = self.plugit.doQuery("test_fileupload", method='POST', files={'test': FileObj()}).json()

        os.unlink(tmpfile)

        assert(retour['file-test'] == p)

    def _build_file(self):

        (handle, tmpfile) = tempfile.mkstemp()
        handle = open(tmpfile, 'wb')
        handle.write("test")
        handle.close()

        class FileObj():
            def temporary_file_path(self):
                return tmpfile
            name = 'test'

        return (tmpfile, FileObj())

    def test_post_param_with_files(self):
        fname, fobj = self._build_file()

        p = str(uuid.uuid4())
        retour = self.plugit.doQuery("test_post", method='POST', postParameters={'post_param': p}, files={'test': fobj}).json()

        os.unlink(fname)

        assert(retour['method'] == 'POST')
        assert(retour['post_param'] == p)

    def test_post_getparam_with_files(self):
        fname, fobj = self._build_file()
        p = str(uuid.uuid4())
        retour = self.plugit.doQuery("test_post", method='POST', getParmeters={'get_param': p}, files={'test': fobj}).json()
        os.unlink(fname)
        assert(retour['method'] == 'POST')
        assert(retour['get_param'] == p)

    def test_post_postparam_list_with_files(self):
        fname, fobj = self._build_file()
        p = [str(uuid.uuid4()), str(uuid.uuid4())]
        retour = self.plugit.doQuery("test_post_list", method='POST', postParameters={'post_param': p}, files={'test': fobj}).json()
        os.unlink(fname)
        assert(retour['method'] == 'POST')
        assert(retour['post_param'] == p)

    def test_extraHeaders_post_with_files(self):
        fname, fobj = self._build_file()
        p = str(uuid.uuid4())

        retour = self.plugit.doQuery("test_extraHeaders", method='POST', extraHeaders={'test': p}, files={'test': fobj}).json()
        os.unlink(fname)
        assert(retour['x-plugit-test'] == p)

    def test_session_post_with_files(self):
        fname, fobj = self._build_file()
        p = str(uuid.uuid4())

        retour = self.plugit.doQuery("test_session", method='POST', session={'test': p}, files={'test': fobj}).json()
        os.unlink(fname)
        assert(retour['x-plugitsession-test'] == p)
        assert(retour['cookie-test'] == p)
