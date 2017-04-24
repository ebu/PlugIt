from flask import Flask

import config
import routes

from params import PI_BASE_URL


app = Flask(getattr(config, 'PI_PROJECT_NAME', 'PlugIT-Project'), static_folder='media', static_url_path=PI_BASE_URL+'media')


def load_actions(act_mod, mail_callback=None):
    routes.load_routes(app, act_mod, mail_callback)
