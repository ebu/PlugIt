"""Test internal functions and features of the proxy"""


import unittest
from nose.tools import *


from django.conf import settings
import django


settings.configure(LOGGING_CONFIG=None, PIAPI_STANDALONE=True, PIAPI_BASEURI="/plugIt/", PIAPI_ORGAMODE=True, PIAPI_REALUSERS=False, PIAPI_PROXYMODE=False, PIAPI_PLUGITMENUACTION='menubar', PIAPI_STANDALONE_URI='http://127.0.0.1:63441', TEMPLATE_DIRS=('tests/templates',), PIAPI_USERDATA=['k'], PIAPI_PLUGITTEMPLATE=None)


from django import template
from django.template import loader
from django.template.base import TemplateSyntaxError
from django.core.cache import cache
from django.test.utils import setup_test_environment, teardown_test_environment
# from django.db.connection.creation import create_test_db, destroy_test_db
from django.test import RequestFactory
import json
import os
import sys
import uuid
import subprocess
import time
import tempfile


class TestBase(unittest.TestCase):
    """Common class for tests"""

    STANDALONE_PROXY = os.path.join('examples', 'standalone_proxy')

    @classmethod
    def setup_class(self):
        """Setup path"""
        sys.path.append(self.STANDALONE_PROXY)

    @classmethod
    def teardown_class(self):
        """Remove added value from path"""
        sys.path.remove(self.STANDALONE_PROXY)


class TestCheckMail(TestBase):

    @classmethod
    def setup_class(self):
        super(TestCheckMail, self).setup_class()
        self.start_popserver()
        self.run_checkmail()
        self.stop_popserver()

    @classmethod
    def start_popserver(self):
        self.p = subprocess.Popen([sys.executable, 'server.py'], cwd='tests/helpers/pop_server', stderr=subprocess.PIPE)

    @classmethod
    def stop_popserver(self):
        (out, err) = self.p.communicate()
        self.output = err

    @classmethod
    def run_checkmail(self):
        self.pop_user = str(uuid.uuid4())
        self.pop_password = str(uuid.uuid4())

        settings.INCOMING_MAIL_HOST = "127.0.0.1"
        settings.INCOMING_MAIL_PORT = 22110
        settings.INCOMING_MAIL_USER = self.pop_user
        settings.INCOMING_MAIL_PASSWORD = self.pop_password
        settings.EBUIO_MAIL_SECRET_HASH = 'secret-for-tests'
        settings.EBUIO_MAIL_SECRET_KEY = 'secret2-for-tests'

        from plugit_proxy.management.commands import check_mail

        mail_handeled = []

        # False plugit object to capture mail sends
        class DummyPlugIt:
            def __init__(self, *args, **kwargs):
                pass

            def newMail(self, data, payload):
                mail_handeled.append((data, payload))
                return True

        check_mail.PlugIt = DummyPlugIt

        check_mail.Command().handle()

        self.mail_handeled = mail_handeled

        # assert(False)

    def test_output(self):
        assert(self.output)

    def test_user(self):
        """Test that the command logged in"""

        assert("USER:%s\n" % (self.pop_user,) in self.output)

    def test_password(self):
        """Test that the command sent the correct password"""

        assert("PASS:%s\n" % (self.pop_password,) in self.output)

    def test_mail1_retrived(self):
        """Mail1 should have been retrivied"""
        assert("RETRIVE:1\n" in self.output)

    def test_mail1_not_deleted(self):
        """Mail1 should not have been deleted"""
        assert("DELETE:1\n" not in self.output)

    def test_mail2_retrived(self):
        """Mail2 should have been retrivied"""
        assert("RETRIVE:2\n" in self.output)

    def test_mail2_not_deleted(self):
        """Mail2 should not have been deleted"""
        assert("DELETE:2\n" not in self.output)

    def test_mail3_retrived(self):
        """Mail3 should have been retrivied"""
        assert("RETRIVE:3\n" in self.output)

    def test_mail3_not_deleted(self):
        """Mail3 should not have been deleted"""
        assert("DELETE:3\n" not in self.output)

    def test_mail4_retrived(self):
        """Mail4 should have been retrivied"""
        assert("RETRIVE:4\n" in self.output)

    def test_mail4_not_deleted(self):
        """Mail4 should not have been deleted"""
        assert("DELETE:4\n" not in self.output)

    def test_mail5_retrived(self):
        """Mail5 should have been retrivied"""
        assert("RETRIVE:5\n" in self.output)

    def test_mail5_not_deleted(self):
        """Mail5 should not have been deleted"""
        assert("DELETE:5\n" not in self.output)

    def test_mail6_retrived(self):
        """Mail6 should have been retrivied"""
        assert("RETRIVE:6\n" in self.output)

    def test_mail6_not_deleted(self):
        """Mail6 should have been deleted"""
        assert("DELETE:6\n" in self.output)

    def test_mail6_handeled(self):
        """Mail6 should has been handeled"""
        assert(('test', 'ThisIsMail6\n\n') in self.mail_handeled)

    def test_mail7_retrived(self):
        """Mail7 should have been retrivied"""
        assert("RETRIVE:7\n" in self.output)

    def test_mail7_not_deleted(self):
        """Mail7 should have been deleted"""
        assert("DELETE:7\n" in self.output)

    def test_mail7_handeled(self):
        """Mail7 should has been handeled"""
        assert(('test', 'ThisIsMail7\n\n') in self.mail_handeled)

    def test_mail891011121314151617_retrived(self):
        """Mail with auto response should have been retrivied"""
        for i in range(8, 18):
            print("Testing", i,)
            assert("RETRIVE:" + str(i) + "\n" in self.output)
            print("OK")

    def test_mail891011121314151617_not_deleted(self):
        """Mail with auto response should have been deleted"""
        for i in range(8, 18):
            print("Testing", i,)
            assert("DELETE:" + str(i) + "\n" in self.output)
            print("OK")

    def test_mail891011121314151617_handeled(self):
        """Mail with auto response should NOT has been handeled"""
        for i in range(8, 18):
            print("Testing", i,)
            assert(('test', 'ThisIsMail%s\n\n' % (str(i),)) not in self.mail_handeled)
            print("OK")


class TestPlugItTags(TestBase):

    @classmethod
    def setup_class(self):
        super(TestPlugItTags, self).setup_class()

        # Handle custom user generation
        settings.PIAPI_USERDATA = ['pk', 'prop1', 'propa']

        self.user_pk = str(uuid.uuid4())
        self.user_prop1 = str(uuid.uuid4())
        self.user_prop2 = str(uuid.uuid4())

        from plugit_proxy import views
        views.bpk_generate_user = views.generate_user

        def _generate_user(pk):

            class DummyUser():
                pk = self.user_pk
                prop1 = self.user_prop1
                prop2 = self.user_prop2

            if pk == self.user_pk:
                return DummyUser()

        views.generate_user = _generate_user

        # Handle template return
        self.bkp_plugIt = views.plugIt
        self.bkp_getPlugItObject = views.getPlugItObject

        class _plugIt():
            def getTemplate(self, action):
                return "{{test_val}}," + action

        def _getPlugItObject(__):
            return _plugIt(), None, None

        views.plugIt = _plugIt()
        views.getPlugItObject = _getPlugItObject

    @classmethod
    def teardown_class(self):
        super(TestPlugItTags, self).teardown_class()

        from plugit_proxy import views

        views.generate_user = views.bpk_generate_user
        views.plugIt = self.bkp_plugIt
        views.getPlugItObject = self.bkp_getPlugItObject

    def test_get_user_return_user(self):
        from plugit_proxy.templatetags.plugit_tags import plugitGetUser

        assert(plugitGetUser(self.user_pk).id)
        assert(not plugitGetUser(self.user_pk * 2).id)

    def test_get_user_return_only_wanted_user_probs(self):
        from plugit_proxy.templatetags.plugit_tags import plugitGetUser

        user = plugitGetUser(self.user_pk)

        assert(user.pk == self.user_pk)
        assert(user.id == self.user_pk)
        assert(user.prop1 == self.user_prop1)
        assert(not hasattr(user, 'prop2'))

    def test_plugit_include(self):

        settings.INSTALLED_APPS = ('plugIt',)
        django.setup()

        action = str(uuid.uuid4())
        test_val = str(uuid.uuid4())

        context = template.Context({'action': action, 'test_val': test_val})

        result = template.Template("""{% load plugit_tags %}{% plugitInclude action %}""").render(context)

        assert(result == "%s,%s" % (test_val, action,))

    def test_plugit_include_error(self):

        settings.INSTALLED_APPS = ('plugIt',)
        django.setup()

        action = str(uuid.uuid4())
        test_val = str(uuid.uuid4())

        context = template.Context({'action': action, 'test_val': test_val})

        try:
            template.Template("""{% load plugit_tags %}{% plugitInclude %}""").render(context)
        except TemplateSyntaxError:
            return

        assert(False)

    def test_plugit_include_security(self):

        settings.INSTALLED_APPS = ('plugIt',)
        settings.PIAPI_STANDALONE = False
        settings.SECRET_FOR_SIGNS = str(uuid.uuid4())
        django.setup()

        action = str(uuid.uuid4())
        test_val = str(uuid.uuid4())
        hpropk = str(uuid.uuid4())
        hproname = str(uuid.uuid4())

        class DummyUser():
            pk = str(uuid.uuid4())
        u = DummyUser()

        import utils
        import app
        app.utils = utils

        hkey = utils.create_secret(hpropk, hproname, u.pk)

        contextok = template.Context({'action': action, 'test_val': test_val, 'ebuio_hpro_pk': hpropk, 'ebuio_hpro_name': hproname, 'ebuio_u': u, 'ebuio_hpro_key': hkey})
        contexterr = template.Context({'action': action, 'test_val': test_val, 'ebuio_hpro_pk': hpropk, 'ebuio_hpro_name': hproname, 'ebuio_u': u, 'ebuio_hpro_key': hkey * 2})

        resultok = template.Template("""{% load plugit_tags %}{% plugitInclude action %}""").render(contextok)
        resulterr = template.Template("""{% load plugit_tags %}{% plugitInclude action %}""").render(contexterr)

        settings.PIAPI_STANDALONE = True

        assert(resultok == "%s,%s" % (test_val, action,))
        assert(resulterr == "")

    def test_plugit_url_target_blank(self):

        settings.INSTALLED_APPS = ('plugIt',)
        django.setup()

        action = str(uuid.uuid4())
        test_val = str(uuid.uuid4())

        context = template.Context({'action': action, 'test_val': test_val})

        result = template.Template("""{% load plugit_tags %}{{ '<a b>' | url_target_blank | safe }}""").render(context)

        assert(result == '<a target="_blank" b>')


class TestPlugItDoQueryTest(TestBase):

    @classmethod
    def setup_class(self):
        super(TestPlugItDoQueryTest, self).setup_class()
        FNULL = open(os.devnull, 'w')
        self.p = subprocess.Popen([sys.executable, 'doquery_server.py'], cwd='tests/helpers', stdout=FNULL, stderr=FNULL)
        time.sleep(0.5)

        from plugit_proxy.plugIt import PlugIt
        self.plugit = PlugIt("http://127.0.0.1:62314")

    @classmethod
    def teardown_class(self):
        super(TestPlugItDoQueryTest, self).teardown_class()
        self.p.kill()

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


class TestPlugIt(TestBase):

    @classmethod
    def setup_class(self):
        super(TestPlugIt, self).setup_class()

        from plugit_proxy.plugIt import PlugIt

        self.plugIt = PlugIt('http://0.0.0.0/')

        myself = self

        def _doQuery(url, method='GET', getParmeters=None, postParameters=None, files=None, extraHeaders={}, session={}):
            myself.lastDoQueryCall = {'url': url, 'method': method, 'getParmeters': getParmeters, 'postParameters': postParameters, 'files': files, 'extraHeaders': extraHeaders, 'session': session}

            class DummyResponse():
                def json(self):
                    return myself.plugIt.toReplyJson()

                @property
                def status_code(self):
                    return myself.plugIt.toReplyStatusCode()

                @property
                def headers(self):
                    return myself.plugIt.toReplyHeaders()

                @property
                def content(self):
                    return json.dumps(self.json())

            return DummyResponse()

        self.plugIt.doQuery = _doQuery

    def test_ping(self):

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'data': self.lastDoQueryCall['url'].split('data=', 1)[1]}

        assert(self.plugIt.ping())

        self.plugIt.toReplyStatusCode = lambda: 404

        assert(not self.plugIt.ping())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'data': self.lastDoQueryCall['url'].split('data=', 1)[1] * 2}

        assert(not self.plugIt.ping())

        assert(self.lastDoQueryCall['url'].startswith('ping'))

    def test_check_version(self):

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'result': 'Ok', 'version': self.plugIt.PI_API_VERSION, 'protocol': self.plugIt.PI_API_NAME}

        assert(self.plugIt.checkVersion())
        assert(self.lastDoQueryCall['url'] == 'version')

        self.plugIt.toReplyJson = lambda: {'result': 'poney', 'version': self.plugIt.PI_API_VERSION, 'protocol': self.plugIt.PI_API_NAME}
        assert(not self.plugIt.checkVersion())

        self.plugIt.toReplyJson = lambda: {'result': 'Ok', 'version': self.plugIt.PI_API_VERSION * 2, 'protocol': self.plugIt.PI_API_NAME}
        assert(not self.plugIt.checkVersion())

        self.plugIt.toReplyJson = lambda: {'result': 'Ok', 'version': self.plugIt.PI_API_VERSION, 'protocol': self.plugIt.PI_API_NAME * 2}
        assert(not self.plugIt.checkVersion())

        self.plugIt.toReplyStatusCode = lambda: 201
        self.plugIt.toReplyJson = lambda: {'result': 'Ok', 'version': self.plugIt.PI_API_VERSION, 'protocol': self.plugIt.PI_API_NAME}

        assert(not self.plugIt.checkVersion())

    def test_new_mail(self):

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'result': 'Ok'}

        message_id = str(uuid.uuid4())
        message = str(uuid.uuid4())

        assert(self.plugIt.newMail(message_id, message))
        assert(self.lastDoQueryCall['url'] == 'mail')
        assert(self.lastDoQueryCall['postParameters'].get('response_id') == message_id)
        assert(self.lastDoQueryCall['postParameters'].get('message') == message)

        self.plugIt.toReplyStatusCode = lambda: 201
        assert(not self.plugIt.newMail(message_id, message))

    def test_media(self):
        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {}

        media = str(uuid.uuid4())

        data, content_type = self.plugIt.getMedia(media)

        assert(data == '{}')
        assert(content_type == 'application/octet-stream')
        assert(self.lastDoQueryCall['url'] == 'media/{}'.format(media))

        self.plugIt.toReplyHeaders = lambda: {'content-type': 'test'}

        data, content_type = self.plugIt.getMedia(media)

        assert(data == '{}')
        assert(content_type == 'test')

        self.plugIt.toReplyStatusCode = lambda: 201
        data, content_type = self.plugIt.getMedia(media)
        assert(not data)
        assert(not content_type)

    def test_meta(self):

        k = str(uuid.uuid4())
        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k}
        self.plugIt.toReplyHeaders = lambda: {'expire': 'Wed, 21 Oct 2015 07:28:00 GMT'}

        data = self.plugIt.getMeta(path)
        assert(self.lastDoQueryCall['url'] == 'meta/{}'.format(path))
        assert(data['k'] == k)

        # Data should not be cached
        self.plugIt.toReplyJson = lambda: {'k2': k}
        data = self.plugIt.getMeta(path)
        assert(data['k2'] == k)

    def test_meta_fail(self):
        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 201
        assert(not self.plugIt.getMeta(path))

    def test_meta_cache(self):

        k = str(uuid.uuid4())
        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k}
        self.plugIt.toReplyHeaders = lambda: {}

        # Data should be cached
        data = self.plugIt.getMeta(path)
        self.plugIt.toReplyJson = lambda: {'k2': k}
        data = self.plugIt.getMeta(path)
        assert(data['k'] == k)

    def test_template(self):

        k = str(uuid.uuid4())
        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k, 'template_tag': '-'}
        self.plugIt.toReplyHeaders = lambda: {}

        data = json.loads(self.plugIt.getTemplate(path))
        assert(self.lastDoQueryCall['url'] == 'template/{}'.format(path))
        assert(data['k'] == k)

        # Data should be cached
        self.plugIt.toReplyJson = lambda: {'k2': k, 'template_tag': '-'}
        data = json.loads(self.plugIt.getTemplate(path))
        assert(data['k'] == k)

    def test_template_fail(self):

        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 201
        assert(not self.plugIt.getTemplate(path))

    def test_template_no_meta_no_template(self):
        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        assert(not self.plugIt.getTemplate(path))

    def test_do_action_normal_mode(self):

        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {}

        assert(self.plugIt.doAction(path) == ({}, {}))
        assert(self.lastDoQueryCall['url'] == 'action/{}'.format(path))

    def test_do_action_proxy_mode(self):

        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {}

        assert(self.plugIt.doAction(path, proxyMode=True) == ("{}", {}))
        assert(self.lastDoQueryCall['url'] == path)

    def test_do_action_proxy_mode_no_remplate(self):

        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k}
        self.plugIt.toReplyHeaders = lambda: {'ebuio-plugit-notemplate': True}

        r, __ = self.plugIt.doAction('', proxyMode=True)

        assert(r.__class__.__name__ == 'PlugItNoTemplate')
        assert(json.loads(r.content)['k'] == k)

    def test_do_action_data(self):

        path = str(uuid.uuid4())
        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k}
        self.plugIt.toReplyHeaders = lambda: {}

        assert(self.plugIt.doAction(path) == ({'k': k}, {}))

    def test_do_action_500(self):
        self.plugIt.toReplyStatusCode = lambda: 500
        assert(self.plugIt.doAction('')[0].__class__.__name__ == 'PlugIt500')

    def test_do_action_fail(self):
        self.plugIt.toReplyStatusCode = lambda: 501
        assert(self.plugIt.doAction('') == (None, {}))

    def test_do_action_session(self):

        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {'Ebuio-PlugIt-SetSession-k': k}
        assert(self.plugIt.doAction('') == ({}, {'k': k}))

    def test_do_action_redirect(self):

        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {'ebuio-plugit-redirect': k}
        r, headers = self.plugIt.doAction('')

        assert(r.__class__.__name__ == 'PlugItRedirect')
        assert(r.url == k)
        assert(not r.no_prefix)
        assert(headers == {})

    def test_do_action_redirect_noprefix(self):

        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {'ebuio-plugit-redirect': k, 'ebuio-plugit-redirect-noprefix': "True"}
        r, headers = self.plugIt.doAction('')

        assert(r.__class__.__name__ == 'PlugItRedirect')
        assert(r.url == k)
        assert(r.no_prefix)
        assert(headers == {})

    def test_do_action_file(self):

        k = str(uuid.uuid4())
        content_type = str(uuid.uuid4())
        content_disposition = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k}
        self.plugIt.toReplyHeaders = lambda: {'ebuio-plugit-itafile': k, 'Content-Type': content_type}
        r, headers = self.plugIt.doAction('')

        assert(r.__class__.__name__ == 'PlugItFile')
        assert(json.loads(r.content)['k'] == k)
        assert(r.content_type == content_type)
        assert(r.content_disposition == '')
        assert(headers == {})

        self.plugIt.toReplyHeaders = lambda: {'ebuio-plugit-itafile': k, 'Content-Type': content_type, 'content-disposition': content_disposition}
        r, headers = self.plugIt.doAction('')
        assert(r.content_disposition == content_disposition)


class TestProxyViews(TestBase):

    process_service = None

    @classmethod
    def setup_class(self):
        super(TestProxyViews, self).setup_class()

        django.setup()
        setup_test_environment()

        from plugit_proxy import views
        from plugit_proxy.plugIt import PlugIt

        self.views = views
        self.PlugIt = PlugIt

        self.factory = RequestFactory()

        self.start_process_service()

    @classmethod
    def teardown_class(self):
        super(TestProxyViews, self).teardown_class()
        teardown_test_environment()

        self.process_service.kill()
        self.process_service = None

    @classmethod
    def start_process_service(self, args=[]):

        if self.process_service:
            self.process_service.kill()

        FNULL = open(os.devnull, 'w')
        self.process_service = subprocess.Popen([sys.executable, 'server.py'] + args, cwd='tests/helpers/flask_server', stdout=FNULL, stderr=FNULL)
        time.sleep(0.5)

    def random_base_url(self):

        new_base_url = str(uuid.uuid4())

        self.views.baseURI_bkp = self.views.baseURI
        self.views.baseURI = new_base_url

        return new_base_url

    def restore_base_url(self):
        self.views.baseURI = self.views.baseURI_bkp

    def build_request(self, path):
        r = self.factory.get(path)
        r.session = {}

        return r

    def test_generate_user_nobody(self):
        assert(not self.views.generate_user(None, None))

    def test_generate_user_ano(self):
        user = self.views.generate_user('ano')
        assert(user)
        assert(not user.is_authenticated())
        assert(not user.ebuio_member)
        assert(not user.ebuio_admin)
        assert(not user.ebuio_orga_member)
        assert(not user.ebuio_orga_admin)

    def test_generate_user_log(self):
        user = self.views.generate_user('log')
        assert(user)
        assert(user.is_authenticated())
        assert(not user.ebuio_member)
        assert(not user.ebuio_admin)
        assert(not user.ebuio_orga_member)
        assert(not user.ebuio_orga_admin)

    def test_generate_user_mem(self):
        user = self.views.generate_user('mem')
        assert(user)
        assert(user.is_authenticated())
        assert(user.ebuio_member)
        assert(not user.ebuio_admin)
        assert(user.ebuio_orga_member)
        assert(not user.ebuio_orga_admin)

    def test_generate_user_adm(self):
        user = self.views.generate_user('adm')
        assert(user)
        assert(user.is_authenticated())
        assert(user.ebuio_member)
        assert(user.ebuio_admin)
        assert(user.ebuio_orga_member)
        assert(user.ebuio_orga_admin)

    def test_generate_user_compat_mode(self):
        user = self.views.generate_user(None, 3)
        assert(user)
        assert(user.is_authenticated())
        assert(not user.ebuio_member)
        assert(not user.ebuio_admin)
        assert(not user.ebuio_orga_member)
        assert(not user.ebuio_orga_admin)

    def test_gen_404(self):
        raison = str(uuid.uuid4())
        url = self.random_base_url()
        usermode = str(uuid.uuid4())

        request = self.build_request('/')
        request.session['plugit-standalone-usermode'] = usermode

        response = self.views.gen404(request, url, raison)

        assert(response)
        assert(response.status_code == 404)
        assert(response.content.strip() == '404,{},{},{}'.format(raison, url, usermode))

        self.restore_base_url()

    def test_gen_500(self):
        url = self.random_base_url()
        usermode = str(uuid.uuid4())

        request = self.build_request('/')
        request.session['plugit-standalone-usermode'] = usermode

        response = self.views.gen500(request, url)

        assert(response)
        assert(response.status_code == 500)
        assert(response.content.strip() == '500,{},{}'.format(url, usermode))

        self.restore_base_url()

    def test_gen_403(self):
        raison = str(uuid.uuid4())
        project = str(uuid.uuid4())
        url = self.random_base_url()
        usermode = str(uuid.uuid4())

        request = self.build_request('/')
        request.session['plugit-standalone-usermode'] = usermode

        response = self.views.gen403(request, url, raison, project)

        assert(response)
        assert(response.status_code == 403)
        assert(response.content.strip() == '403,{},{},{},{}'.format(raison, url, usermode, project))

        self.restore_base_url()

    def test_cache_key_no_cache(self):
        assert(not self.views.get_cache_key(None, {}, None, None))

    def test_cache_key_zero_cache_time(self):
        assert(not self.views.get_cache_key(None, {'cache_time': 0}, None, None))

    def test_cache_key_cache_time(self):
        assert(self.views.get_cache_key(self.build_request('/'), {'cache_time': 1, 'template_tag': ''}, None, None))

    def test_cache_key_varies_on_path(self):
        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        headers = {'cache_time': 1, 'template_tag': ''}

        assert(self.views.get_cache_key(self.build_request(k), headers, None, None) == self.views.get_cache_key(self.build_request(k), headers, None, None))
        assert(self.views.get_cache_key(self.build_request(k), headers, None, None) != self.views.get_cache_key(self.build_request(k2), headers, None, None))

    def test_cache_key_varies_on_template_tag(self):
        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        request = self.build_request('/')

        assert(self.views.get_cache_key(request, {'cache_time': 1, 'template_tag': k}, None, None) == self.views.get_cache_key(request, {'cache_time': 1, 'template_tag': k}, None, None))
        assert(self.views.get_cache_key(request, {'cache_time': 1, 'template_tag': k}, None, None) != self.views.get_cache_key(request, {'cache_time': 1, 'template_tag': k2}, None, None))

    def test_cache_key_varies_on_orga(self):

        class O1:
            pk = str(uuid.uuid4())

        class O2:
            pk = str(uuid.uuid4())

        headers = {'cache_time': 1, 'template_tag': ''}
        request = self.build_request('/')

        assert(self.views.get_cache_key(request, headers, False, O1) == self.views.get_cache_key(request, headers, False, O1))
        assert(self.views.get_cache_key(request, headers, False, O1) == self.views.get_cache_key(request, headers, False, O2))
        assert(self.views.get_cache_key(request, headers, True, O1) == self.views.get_cache_key(request, headers, True, O1))
        assert(self.views.get_cache_key(request, headers, True, O1) != self.views.get_cache_key(request, headers, True, O2))

    def test_cache_key_varies_on_user(self):

        class U1:
            pk = str(uuid.uuid4())

        class U2:
            pk = str(uuid.uuid4())

        r1 = self.build_request('/')
        r2 = self.build_request('/')

        r1.user = U1()
        r2.user = U2()

        headers = {'cache_time': 1, 'template_tag': ''}

        assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r1, headers, False, False))
        assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r2, headers, False, False))

        headers = {'cache_time': 1, 'template_tag': '', 'cache_by_user': False}

        assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r1, headers, False, False))
        assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r2, headers, False, False))

        headers = {'cache_time': 1, 'template_tag': '', 'cache_by_user': True}

        assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r1, headers, False, False))
        assert(self.views.get_cache_key(r1, headers, False, False) != self.views.get_cache_key(r2, headers, False, False))

        for should_cache in ['only_logged_user', 'only_member_user', 'only_admin_user', 'only_orga_member_user', 'only_orga_admin_user']:
            headers = {'cache_time': 1, 'template_tag': '', should_cache: True}

            assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r1, headers, False, False))
            assert(self.views.get_cache_key(r1, headers, False, False) != self.views.get_cache_key(r2, headers, False, False))

            headers = {'cache_time': 1, 'template_tag': '', 'cache_by_user': False, should_cache: True}

            assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r1, headers, False, False))
            assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r2, headers, False, False))

            headers = {'cache_time': 1, 'template_tag': '', 'cache_by_user': True, should_cache: True}

            assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r1, headers, False, False))
            assert(self.views.get_cache_key(r1, headers, False, False) != self.views.get_cache_key(r2, headers, False, False))

    def batch_check_rights_and_access(self, request, meta, rights):

        for right, value in rights.items():
            request.user = self.views.generate_user(right)
            response = self.views.check_rights_and_access(request, meta)

            if value:
                if not response or response.status_code != value:
                    print("Excepted {}, got {}".format(value, response.status_code if response else 'Nothing'))
                    assert(False)
            else:
                if response:
                    print("Excepted nothing, got {}".format(response.status_code if response else 'Nothing'))
                    assert(False)

    def test_rights_and_access_nothing_needed(self):

        self.batch_check_rights_and_access(self.build_request('/'), {}, {
            'ano': False,
            'log': False,
            'mem': False,
            'adm': False,
        })

    def test_check_rights_and_access_logged_in(self):

        meta = {'only_logged_user': True}

        self.batch_check_rights_and_access(self.build_request('/'), meta, {
            'ano': 403,
            'log': False,
            'mem': False,
            'adm': False,
        })

    def test_check_rights_and_access_member(self):

        meta = {'only_member_user': True}

        self.batch_check_rights_and_access(self.build_request('/'), meta, {
            'ano': 403,
            'log': 403,
            'mem': False,
            'adm': False,
        })

    def test_check_rights_and_access_admin(self):

        meta = {'only_admin_user': True}

        self.batch_check_rights_and_access(self.build_request('/'), meta, {
            'ano': 403,
            'log': 403,
            'mem': 403,
            'adm': False,
        })

    def test_check_rights_and_access_orga_member(self):

        meta = {'only_orga_member_user': True}

        self.batch_check_rights_and_access(self.build_request('/'), meta, {
            'ano': 403,
            'log': 403,
            'mem': False,
            'adm': False,
        })

    def test_check_rights_and_access_orga_admin(self):

        meta = {'only_orga_admin_user': True}

        self.batch_check_rights_and_access(self.build_request('/'), meta, {
            'ano': 403,
            'log': 403,
            'mem': 403,
            'adm': False,
        })

    def test_check_rights_and_access_address_in_network(self):

        request = self.build_request('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'

        meta = {'address_in_networks': ['127.0.0.1/32']}

        self.batch_check_rights_and_access(request, meta, {
            'ano': False,
            'log': False,
            'mem': False,
            'adm': False,
        })

        request = self.build_request('/')
        request.META['REMOTE_ADDR'] = '42.42.42.42'

        self.batch_check_rights_and_access(request, meta, {
            'ano': 403,
            'log': 403,
            'mem': 403,
            'adm': 403,
        })

        meta = {'address_in_networks': ['127.0.0.1/32', '42.42.42.0/24']}

        self.batch_check_rights_and_access(request, meta, {
            'ano': False,
            'log': False,
            'mem': False,
            'adm': False,
        })

        request = self.build_request('/')
        request.META['REMOTE_ADDR'] = ''

        self.batch_check_rights_and_access(request, meta, {
            'ano': 403,
            'log': 403,
            'mem': 403,
            'adm': 403,
        })

    def test_address_in_network(self):

        # Test common cases
        assert(self.views.is_address_in_network('127.0.0.1', '127.0.0.1/32'))
        assert(self.views.is_address_in_network('127.0.0.1', '127.0.0.1/24'))
        assert(self.views.is_address_in_network('127.0.0.1', '127.0.0.1/16'))
        assert(self.views.is_address_in_network('127.0.0.1', '127.0.0.1/8'))
        assert(self.views.is_address_in_network('127.0.0.1', '127.0.0.1/0'))

        assert(not self.views.is_address_in_network('127.0.0.2', '127.0.0.1/32'))
        assert(self.views.is_address_in_network('127.0.0.2', '127.0.0.1/24'))
        assert(self.views.is_address_in_network('127.0.0.2', '127.0.0.1/16'))
        assert(self.views.is_address_in_network('127.0.0.2', '127.0.0.1/8'))
        assert(self.views.is_address_in_network('127.0.0.2', '127.0.0.1/0'))

        assert(not self.views.is_address_in_network('127.0.1.1', '127.0.0.1/32'))
        assert(not self.views.is_address_in_network('127.0.1.1', '127.0.0.1/24'))
        assert(self.views.is_address_in_network('127.0.1.1', '127.0.0.1/16'))
        assert(self.views.is_address_in_network('127.0.1.1', '127.0.0.1/8'))
        assert(self.views.is_address_in_network('127.0.1.1', '127.0.0.1/0'))

        assert(not self.views.is_address_in_network('127.1.1.1', '127.0.0.1/32'))
        assert(not self.views.is_address_in_network('127.1.1.1', '127.0.0.1/24'))
        assert(not self.views.is_address_in_network('127.1.1.1', '127.0.0.1/16'))
        assert(self.views.is_address_in_network('127.1.1.1', '127.0.0.1/8'))
        assert(self.views.is_address_in_network('127.1.1.1', '127.0.0.1/0'))

        assert(not self.views.is_address_in_network('128.1.1.1', '127.0.0.1/32'))
        assert(not self.views.is_address_in_network('128.1.1.1', '127.0.0.1/24'))
        assert(not self.views.is_address_in_network('128.1.1.1', '127.0.0.1/16'))
        assert(not self.views.is_address_in_network('128.1.1.1', '127.0.0.1/8'))
        assert(self.views.is_address_in_network('128.1.1.1', '127.0.0.1/0'))

    def test_caching(self):

        cache_key = str(uuid.uuid4())
        result = {'r': uuid.uuid4()}
        menu = {'r': uuid.uuid4()}

        class Context():
            dicts = [{'r': uuid.uuid4(), 'csrf_token': uuid.uuid4()}]

        meta = {'cache_time': 1}

        self.views.cache_if_needed(cache_key, result, menu, Context(), meta)

        r, m, c = self.views.find_in_cache(cache_key)

        assert(r == result)
        assert(m == menu)
        assert(c['r'] == Context.dicts[0]['r'])
        assert('csrf_token' not in c)

        # Unknows keys shouldn't be cached
        r, m, c = self.views.find_in_cache(cache_key * 2)
        assert(not r)
        assert(not m)
        assert(not c)

        # No key, no cache
        r, m, c = self.views.find_in_cache(None)
        assert(not r)
        assert(not m)
        assert(not c)

        # Caching should works without a menu
        self.views.cache_if_needed(cache_key, result, None, Context(), meta)

        r, m, c = self.views.find_in_cache(cache_key)
        assert(r)
        assert(not m)
        assert(c)

    def test_build_base_parmeters_get(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        r = self.factory.get('/', {'k': k, 'ebuio_k': k2})

        get, post, files = self.views.build_base_parameters(r)

        assert(get['k'] == k)
        assert('ebuio_k' not in get)
        assert(not post)

    def test_build_base_parmeters_get_list(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        r = self.factory.get('/', {'k': [k, k2]})

        get, post, files = self.views.build_base_parameters(r)

        assert(get['k'] == [k, k2])

    def test_build_base_parmeters_post(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        r = self.factory.post('/', {'k': k, 'ebuio_k': k2})

        get, post, files = self.views.build_base_parameters(r)

        assert(not get)
        assert(post['k'] == k)
        assert('ebuio_k' not in post)

    def test_build_base_parmeters_post_list(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        r = self.factory.post('/', {'k': [k, k2]})

        get, post, files = self.views.build_base_parameters(r)

        assert(post['k'] == [k, k2])

    def test_build_base_parmeters_post_and_get(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        r = self.factory.post('/?k={}'.format(k), {'k': k2})

        get, post, files = self.views.build_base_parameters(r)

        assert(get['k'] == k)
        assert(post['k'] == k2)

    def test_build_base_parmeters_post_files(self):

        with open('tests/helpers/flask_server/media/testfile1', 'rb') as f:
            r = self.factory.post('/', {'k': f, 'ebuio_k': f})

        get, post, files = self.views.build_base_parameters(r)

        assert(not get)
        assert(not post)
        assert('k' in files)
        assert('ebuio_k' not in files)

    def test_build_user_requested_parameters(self):

        settings.PIAPI_USERDATA = ['k']

        k = str(uuid.uuid4())

        class U():
            pass

        r = self.build_request('/')
        r.user = U()
        r.user.k = k

        get, post, files = self.views.build_user_requested_parameters(r, {'user_info': ['k']})

        assert(get['ebuio_u_k'] == k)
        assert(not post)
        assert(not files)

    def test_build_user_requested_parameters_post(self):

        settings.PIAPI_USERDATA = ['k']

        k = str(uuid.uuid4())

        class U():
            pass

        r = self.factory.post('/')
        r.user = U()
        r.user.k = k

        get, post, files = self.views.build_user_requested_parameters(r, {'user_info': ['k']})

        assert(not get)
        assert(post['ebuio_u_k'] == k)
        assert(not files)

    def test_build_user_requested_parameters_unknown(self):

        settings.PIAPI_USERDATA = []

        k = str(uuid.uuid4())

        class U():
            pass

        r = self.factory.post('/')
        r.user = U()
        r.user.k = k

        # Should raise exception
        try:
            get, post, files = self.views.build_user_requested_parameters(r, {'user_info': ['k']})
        except Exception:
            return

        assert(False)

    def test_build_user_requested_parameters_not_a_prop(self):

        settings.PIAPI_USERDATA = ['k']

        class U():
            pass

        r = self.factory.post('/')
        r.user = U()

        # Should raise exception
        try:
            get, post, files = self.views.build_user_requested_parameters(r, {'user_info': ['k']})
        except Exception:
            return

        assert(False)

    def test_build_user_requested_parameters_prop_false(self):

        settings.PIAPI_USERDATA = ['k']

        class U():
            pass

        r = self.factory.post('/')
        r.user = U()
        r.user.k = None

        get, post, files = self.views.build_user_requested_parameters(r, {'user_info': ['k']})

        assert(not get)
        assert(not post['ebuio_u_k'])
        assert(not files)

    def test_build_orga_parameters_no_orga(self):

        assert(self.views.build_orga_parameters(None, False, False) == ({}, {}, {}))
        assert(self.views.build_orga_parameters(None, True, False) == ({}, {}, {}))
        assert(self.views.build_orga_parameters(None, False, True) == ({}, {}, {}))

    def test_build_orga_parameters_orga(self):

        class O():
            pk = str(uuid.uuid4())

        assert(self.views.build_orga_parameters(self.factory.get('/'), True, O()) == ({'ebuio_orgapk': O.pk}, {}, {}))
        assert(self.views.build_orga_parameters(self.factory.post('/'), True, O()) == ({}, {'ebuio_orgapk': O.pk}, {}))

    def test_build_parameters(self):

        settings.PIAPI_USERDATA = ['k']

        class O():
            pk = str(uuid.uuid4())

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        class U():
            pass

        r = self.factory.get('/', {'k2': k2})
        r.user = U()
        r.user.k = k

        get, post, files = self.views.build_parameters(r, {'user_info': ['k']}, True, O())

        assert(get['ebuio_orgapk'] == O.pk)
        assert(get['k2'] == k2)
        assert(get['ebuio_u_k'] == k)
        assert(not post)
        assert(not files)

    def test_build_extra_headers(self):

        k = str(uuid.uuid4())
        uri = self.random_base_url()

        assert(not self.views.build_extra_headers(None, False, False, None))

        settings.PIAPI_USERDATA = ['k']

        class U():
            pass

        r = self.factory.get('/')
        r.user = U()
        r.user.k = k

        headers = self.views.build_extra_headers(r, True, False, None)

        assert(headers['user_k'] == k)
        assert(headers['base_url'] == uri)
        assert('orga_pk' not in headers)
        assert('orga_name' not in headers)
        assert('orga_codops' not in headers)

        class O():
            pk = str(uuid.uuid4())
            name = str(uuid.uuid4())
            ebu_codops = str(uuid.uuid4())

        headers = self.views.build_extra_headers(r, True, True, O())
        assert(headers['orga_pk'] == O.pk)
        assert(headers['orga_name'] == O.name)
        assert(headers['orga_codops'] == O.ebu_codops)

        self.restore_base_url()

    def test_handle_special_case_no_data(self):
        assert(self.views.handle_special_cases(self.build_request('/'), None, None, {}).status_code == 404)

    def test_handle_special_case_empty_data(self):
        assert(not self.views.handle_special_cases(self.build_request('/'), {}, None, {}))

    def test_handle_special_case_500(self):

        class PlugIt500():
            pass

        assert(self.views.handle_special_cases(self.build_request('/'), PlugIt500(), None, {}).status_code == 500)

    def test_handle_special_case_redirect(self):

        class PlugItRedirect():
            def __init__(self, url, no_prefix=False):
                self.url = url
                self.no_prefix = no_prefix

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        r = self.views.handle_special_cases(self.build_request('/'), PlugItRedirect(k), k2, {})
        assert(r.status_code == 302)
        assert(r['Location'] == '{}{}'.format(k2, k))

        r = self.views.handle_special_cases(self.build_request('/'), PlugItRedirect(k, True), k2, {})
        assert(r.status_code == 302)
        assert(r['Location'] == k)

    def test_handle_special_case_file(self):

        class PlugItFile():
            content = str(uuid.uuid4())
            content_type = str(uuid.uuid4())
            content_disposition = str(uuid.uuid4())

        r = self.views.handle_special_cases(self.build_request('/'), PlugItFile(), None, {})

        assert(r.content == PlugItFile.content)
        assert(r['Content-Type'] == PlugItFile.content_type)
        assert(r['Content-Disposition'] == PlugItFile.content_disposition)

    def test_handle_special_case_no_template(self):

        class PlugItNoTemplate():
            content = str(uuid.uuid4())

        r = self.views.handle_special_cases(self.build_request('/'), PlugItNoTemplate(), None, {})

        assert(r.content == PlugItNoTemplate.content)

    def test_handle_special_case_json_1(self):

        k = str(uuid.uuid4())

        r = self.views.handle_special_cases(self.build_request('/'), {'k': k}, None, {'json_only': True})

        assert(r.content == json.dumps({'k': k}))
        assert('json' not in r['Content-Type'])

    def test_handle_special_case_json_2(self):

        k = str(uuid.uuid4())

        request = self.build_request('/')
        request.META['HTTP_ACCEPT'] = 'text/json'

        r = self.views.handle_special_cases(request, {'k': k}, None, {'json_only': True})

        assert(r.content == json.dumps({'k': k}))
        assert('json' in r['Content-Type'])

    def test_handle_special_case_xml(self):

        k = str(uuid.uuid4())

        r = self.views.handle_special_cases(self.build_request('/'), {'xml': k}, None, {'xml_only': True})

        assert(r.content == k)

    def test_build_final_template_no_template(self):

        k = str(uuid.uuid4())

        assert(self.views.build_final_response(None, {'no_template': True}, k, None, None, None, None).content == k)

    def test_build_final_template_proxy(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())
        k3 = str(uuid.uuid4())

        assert(self.views.build_final_response(self.build_request('/'), {}, k, k2, None, True, k3).content.strip() == "base,{},{},{}".format(k, k2, k3))

    def test_build_final_template(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())
        k3 = str(uuid.uuid4())

        assert(self.views.build_final_response(self.build_request('/'), {}, k, k2, None, False, k3).content.strip() == "plugitbase,{},{},{}".format(k, k2, k3))

    def test_render_data_proxy(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        tpl = "{}{}~__PLUGIT_CSRF_TOKEN__~{}".format(k, "{", "}")

        assert(self.views.render_data({'csrf_token': k2}, None, True, tpl) == ("{}{}".format(k, k2), None))

    def test_render_data(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())
        menu = str(uuid.uuid4())

        tpl = "{}{}k2{}{}% block menubar %{}menu{}% endblock %{}".format(k, "{{", "}}", "{", "}{{", "}}{", "}")

        assert(self.views.render_data(self.views.Context({'k2': k2, 'menu': menu}), tpl, False, None) == ("{}{}{}".format(k, k2, menu), menu))

    def test_build_context(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())
        k3 = str(uuid.uuid4())
        url = self.random_base_url()

        class U:
            pk = str(uuid.uuid4())

        request = self.build_request('/')
        request.session['plugit-standalone-usermode'] = k
        request.user = U()

        result = self.views.build_context(request, {'k2': k2}, None, False, None, None)

        assert(result['ebuio_baseUrl'] == url)
        assert(result['ebuio_u'].id == U.pk)
        assert(result['ebuio_u'].pk == U.pk)
        assert(result['ebuio_userMode'] == k)
        assert(not result['ebuio_realUsers'])
        assert(not result['ebuio_orgamode'])
        assert(result['k2'] == k2)
        assert('csrf_token' in result)
        assert('MEDIA_URL' in result)
        assert('STATIC_URL' in result)

        result = self.views.build_context(request, {'k2': k2}, None, True, k3, None)
        assert(result['ebuio_orgamode'])
        assert(result['ebuio_orga'] == k3)

        self.restore_base_url()

    def test_get_template_proxy(self):
        assert(self.views.get_template(None, None, None, True) == (None, None))

    def test_get_template(self):
        request = self.build_request('/')
        assert(self.views.get_template(request, "", {}, False) == ('home_template\n', None))

    def test_get_template_404(self):
        request = self.build_request('/')
        template, exception = self.views.get_template(request, "_", {}, False)

        assert(not template)
        assert(exception)
        assert(exception.status_code == 404)

    def test_session(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        request = self.build_request('/')

        self.views.update_session(request, {'k': k}, 1)
        retour = self.views.get_current_session(request, 1)
        assert(retour.get('k') == k)

        self.views.update_session(request, {'k': k2}, 2)
        retour = self.views.get_current_session(request, 1)
        assert(retour.get('k') == k)
        retour = self.views.get_current_session(request, 2)
        assert(retour.get('k') == k2)

    def test_main_view_basic(self):
        settings.PIAPI_USERDATA = ['pk']
        assert(self.views.main(self.build_request('/'), 'test_main').content.strip() == "ok")

    def test_main_view_basic_404(self):
        settings.PIAPI_USERDATA = ['pk']
        assert(self.views.main(self.build_request('/'), '_').status_code == 404)

    def test_main_view_concurent_settings(self):
        settings.PIAPI_REALUSERS = True
        assert(self.views.main(self.build_request('/'), 'test_main').status_code == 404)
        settings.PIAPI_REALUSERS = False

    def test_main_view_proxy_mode(self):
        settings.PIAPI_PROXYMODE = True
        assert(self.views.main(self.build_request('/'), 'action/test_main').content.strip().startswith('base,'))
        settings.PIAPI_PROXYMODE = False

    def test_main_view_proxy_mode_404(self):
        settings.PIAPI_PROXYMODE = True
        assert(self.views.main(self.build_request('/'), '_').status_code == 404)
        settings.PIAPI_PROXYMODE = False

    def test_main_view_cache(self):
        before = self.views.main(self.build_request('/'), 'cacheTime').content.strip().split('\n')[0]
        time.sleep(1)
        after = self.views.main(self.build_request('/'), 'cacheTime').content.strip().split('\n')[0]
        assert(before == after)

    def test_main_view_access(self):

        self.views.check_rights_and_access_bpk = self.views.check_rights_and_access

        class DummyError():
            pass

        def check_rights_and_access(*args, **kwargs):
            return DummyError()

        self.views.check_rights_and_access = check_rights_and_access

        assert(isinstance(self.views.main(self.build_request('/'), 'test_main'), DummyError))

        self.views.check_rights_and_access = self.views.check_rights_and_access_bpk

    def test_main_view_get_menu(self):
        assert(self.views.main(self.build_request('/'), 'test_main', None, True).strip() == "")

    def test_main_view_template(self):

        self.views.get_template_bpk = self.views.get_template

        class DummyError():
            pass

        def get_template(*args, **kwargs):
            return (None, DummyError())

        self.views.get_template = get_template

        assert(isinstance(self.views.main(self.build_request('/'), 'test_main'), DummyError))

        self.views.get_template = self.views.get_template_bpk

    def test_media_view(self):
        assert(self.views.media(self.build_request('/'), 'testfile2').content.strip() == "This is test file 2 !")

    def test_media_view_404(self):
        try:
            self.views.media(self.build_request('/'), '_')
        except Exception:
            return True

        assert(False)  # Exception should have been raised

    def test_set_user_view(self):
        r = self.factory.get('/', {'mode': 'ano'})
        r.session = {}
        self.views.setUser(r)

        self.views.main(r, 'test_set_user')
        result = self.views.main(r, 'test_set_user')
        assert(not r.user.pk)
        assert(result.content.strip() == "None")

        r = self.factory.get('/', {'mode': 'log'})
        r.session = {}
        self.views.setUser(r)

        result = self.views.main(r, 'test_set_user')
        assert(r.user.pk == -1)
        assert(result.content.strip() == "-1")

    def test_set_user_standalone(self):
        settings.PIAPI_STANDALONE = False

        try:
            self.views.setUser(self.build_request('/'))
        except:
            settings.PIAPI_STANDALONE = True
            return True

        assert(False)  # Excpetion should have been raised

    def test_set_user_real(self):
        settings.PIAPI_REALUSERS = True

        try:
            self.views.setUser(self.build_request('/'))
        except:
            settings.PIAPI_REALUSERS = False
            return True

        assert(False)  # Excpetion should have been raised

    def test_set_orga(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        r = self.factory.get('/', {'pk': k, 'name': k2})
        r.session = {}
        self.views.setOrga(r)
        assert(self.views.main(r, 'test_get_orga').content.strip() == "{},{}".format(k, k2))

    def test_check_api_key(self):

        k = str(uuid.uuid4())
        assert(self.views.check_api_key(self.build_request('/'), k, None))

    def test_home(self):

        self.views.main_bkp = self.views.main

        class MainProbe():
            pass

        def main(*args, **kwargs):
            return MainProbe()

        self.views.main = main

        assert(isinstance(self.views.home(self.build_request('/'), None), MainProbe))

        self.views.main = self.views.main_bkp
