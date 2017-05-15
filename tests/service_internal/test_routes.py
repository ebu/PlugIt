from _utils import TestBase


from nose.tools import *


from werkzeug.exceptions import NotFound
from werkzeug.routing import Map
import json


class TestRoutes(TestBase):
    """Test routes.py"""

    @classmethod
    def setup_class(cls):
        super(TestRoutes, cls).setup_class()

        cls.load_routes()

    @classmethod
    def load_routes(cls, with_mail_callback=True):

        import plugit

        class DummyActions:
            @plugit.utils.action(route="/", template="home.html")
            def dummy_action(request):
                return {}

        plugit.app.url_map = Map()
        plugit.app.view_functions = {}
        plugit.load_actions(DummyActions, cls.mail_callback if with_mail_callback else None)

        cls.app = plugit.app

    def patch_view(self, ip='127.0.0.1', dont_jsonify=False, args=None):
        """Patch the plugit view with special callbacks"""

        from plugit import routes
        import json

        self.plugitroutes = routes

        self.bkp_request = self.plugitroutes.request
        self.bkp_jsonfy = self.plugitroutes.jsonify

        myself = self

        class R():
            remote_addr = ip
            headers = {}
            args = {}
            form = {}
            self = myself

        if args:
            R.args = args
            R.form = args

        def false_jsonfy(**obj):
            if dont_jsonify:
                return obj
            return json.dumps(obj)

        self.plugitroutes.request = R()
        self.plugitroutes.jsonify = false_jsonfy

    def unpatch_view(self):
        """Revert changes done to the view"""

        self.plugitroutes.request = self.bkp_request
        self.plugitroutes.jsonify = self.bkp_jsonfy

    def get_rule_by_path(self, path):

        for rule in self.app.url_map.iter_rules():
            if str(rule) == path:
                return rule, self.app.view_functions[rule.endpoint]

    def test_ping_vue_created(self):
        assert(self.get_rule_by_path('/ping'))

    def test_ping_vue_ping(self):

        rule, view = self.get_rule_by_path('/ping')

        self.patch_view(args={'data': 'p'})
        r = json.loads(view())
        self.unpatch_view()

        assert(r['data'] == 'p')

    def test_ping_vue_ip(self):

        from plugit import utils

        backup_allowed = utils.PI_ALLOWED_NETWORKS
        utils.PI_ALLOWED_NETWORKS = ['127.0.0.0/8']

        self.patch_view('1.2.3.4')

        rule, view = self.get_rule_by_path('/ping')

        try:
            view()
        except NotFound:
            self.unpatch_view()
            utils.PI_ALLOWED_NETWORKS = backup_allowed
            return  # Ok :)

        self.unpatch_view()
        utils.PI_ALLOWED_NETWORKS = backup_allowed

        assert(False)

    def test_version_vue_created(self):
        assert(self.get_rule_by_path('/version'))

    def test_version_vue_version(self):

        rule, view = self.get_rule_by_path('/version')

        self.patch_view()
        r = json.loads(view())
        self.unpatch_view()

        assert(r['result'] == 'Ok')
        assert(r['version'] == self.plugitroutes.PI_API_VERSION)
        assert(r['protocol'] == self.plugitroutes.PI_API_NAME)

    def test_mail_vue_created(self):
        assert(self.get_rule_by_path('/mail'))

    def test_mail_vue_mail_no_response(self):

        rule, view = self.get_rule_by_path('/mail')

        self.patch_view(args={'response_id': ''})
        r = json.loads(view())
        self.unpatch_view()

        print(r)

        assert(r['result'] == 'Error')

    @staticmethod
    def mail_callback(request):
        request.self.mail_called = True
        request.self.mail_response_id = request.form['response_id']
        return '{"result": "OkCallback"}'

    def test_mail_vue_mail_callback(self):
        TestRoutes.load_routes()

        rule, view = self.get_rule_by_path('/mail')

        self.patch_view(args={'response_id': '42'})
        self.mail_called = False
        self.mail_response_id = False
        r = json.loads(view())
        self.unpatch_view()

        assert(r['result'] == 'OkCallback')
        assert(self.mail_called)
        assert(self.mail_response_id == '42')

    def test_mail_vue_mail_nocallback(self):
        TestRoutes.load_routes(False)

        rule, view = self.get_rule_by_path('/mail')

        self.patch_view(args={'response_id': '42'})
        self.mail_called = False
        self.mail_response_id = False
        r = json.loads(view())
        self.unpatch_view()

        assert(r['result'] == 'Ok')
        assert(not self.mail_called)
        assert(self.mail_response_id != '42')

    def test_mail_vue_ip(self):

        from plugit import utils

        backup_allowed = utils.PI_ALLOWED_NETWORKS
        utils.PI_ALLOWED_NETWORKS = ['127.0.0.0/8']

        self.patch_view('1.2.3.4')

        rule, view = self.get_rule_by_path('/mail')

        try:
            view()
        except NotFound:
            self.unpatch_view()
            utils.PI_ALLOWED_NETWORKS = backup_allowed
            return  # Ok :)

        self.unpatch_view()
        utils.PI_ALLOWED_NETWORKS = backup_allowed

        assert(False)

    def test_meta_view_created(self):
        assert(self.get_rule_by_path('/meta/'))

    def test_template_view_created(self):
        assert(self.get_rule_by_path('/template/'))

    def test_action_view_created(self):
        assert(self.get_rule_by_path('/action/'))
