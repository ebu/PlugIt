#!/usr/bin/env python
# -*- coding: utf-8 -*-

import plugit
import actions
import config

if __name__ == "__main__":
    plugit.load_actions(actions)

    plugit.app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_URL

    plugit.app.run(host="0.0.0.0", debug=plugit.params.DEBUG, threaded=True)
