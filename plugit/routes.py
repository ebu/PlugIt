from params import PI_BASE_URL, PI_API_VERSION, PI_API_NAME
from views import request, check_ip, jsonify, MetaView, TemplateView, ActionView


def load_routes(app, actions):

    @app.route(PI_BASE_URL + "ping")
    def ping():
        """The ping method: Just return the data provided"""

        if not check_ip(request):
            return

        return jsonify(data=request.args.get('data', ''))

    @app.route(PI_BASE_URL + "version")
    def version():
        """The version method: Return current information about the version"""
        return jsonify(result='Ok', version=PI_API_VERSION, protocol=PI_API_NAME)

    @app.route(PI_BASE_URL + "mail", methods=['POST'])
    def mail():
        """The mail method: Process mail handling"""
        return jsonify(result='Ok')

    # Register the 3 URLs (meta, template, action) for each actions
    # We test for each element in the module actions if it's an action
    # (added by the decorator in utils)
    for act in dir(actions):
        obj = getattr(actions, act)
        if hasattr(obj, 'pi_api_action') and obj.pi_api_action and not hasattr(obj.pi_api_action, '__call__'):
            # We found an action and we can now add it to our routes

            # Meta
            app.add_url_rule(
                '{}meta{}'.format(PI_BASE_URL, obj.pi_api_route),
                view_func=MetaView.as_view('meta_{}'.format(act), action=obj))

            # Template
            app.add_url_rule(
                '{}template{}'.format(PI_BASE_URL, obj.pi_api_route),
                view_func=TemplateView.as_view('template_{}'.format(act), action=obj))

            # Action
            app.add_url_rule(
                '{}action{}'.format(PI_BASE_URL, obj.pi_api_route),
                view_func=ActionView.as_view('action_{}'.format(act), action=obj),
                methods=obj.pi_api_methods)
