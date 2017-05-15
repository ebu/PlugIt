from _utils import TestBase

from django.conf import settings
import django


from django import template
from django.template.base import TemplateSyntaxError
import uuid


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
