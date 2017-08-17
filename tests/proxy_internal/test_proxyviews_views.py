from test_proxyviews import TestProxyViews


from django.conf import settings
import uuid
import time


class TestProxyViewsViews(TestProxyViews):

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

    def test_main_view_options(self):
        settings.PIAPI_USERDATA = ['pk']
        r = self.views.main(self.build_request('/', 'OPTIONS'), 'crossdomain')
        assert(r.status_code == 200)
        assert(r.content.strip() == "")
        assert(r['Access-Control-Allow-Origin'] == 'test')

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
