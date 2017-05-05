from flask import Flask

import config
import routes

from params import PI_BASE_URL


app = Flask(
    getattr(config, 'PI_PROJECT_NAME', 'PlugIT-Project'),
    static_folder='media',
    static_url_path='{}media'.format(PI_BASE_URL)
)


def load_actions(act_mod, mail_callback=None):
    """Initialize routes of the flask application.

    Args:
        act_mod: The module with all actions
        mail_callback: A function to call when the proxy inform about a mail reply. The function must takes a request argument as parameter
    """

    routes.load_routes(app, act_mod, mail_callback)
