#!/usr/bin/env python
# -*- coding: utf-8 -*-

import actions

import sys
sys.path.append('../../../')

import plugit

if 'ip' in sys.argv:
    plugit.utils.PI_ALLOWED_NETWORKS = ['1.2.3.4']

if 'baseurl' in sys.argv:
    plugit.PI_BASE_URL = '/baseurl/'
    plugit.routes.PI_BASE_URL = '/baseurl/'

if __name__ == "__main__":
    plugit.load_actions(actions)
    plugit.app.run(debug=False, port=int(sys.argv[1]))
