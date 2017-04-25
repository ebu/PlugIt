"""Test internal functions and features of the proxy"""


import unittest
from nose.tools import *


from django.conf import settings
import django


settings.configure(LOGGING_CONFIG=None, PIAPI_STANDALONE=True, PIAPI_STANDALONE_URI="", PIAPI_BASEURI="")


from django import template
from django.template import loader
from django.template.base import TemplateSyntaxError
from django.core.cache import cache
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
        self.bkp_generate = views.generate_user

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
        views.generate_user = self.bkp_generate
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


# Todo: views
