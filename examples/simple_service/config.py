import os

API_URL = os.environ.get('PLUGIT_API_URL', '')

# For database
SQLALCHEMY_URL = os.environ.get('PLUGIT_DATABASE', 'sqlite://test.sqlite')

DEBUG = bool(os.environ.get('PLUGIT_DEBUG', False))

PI_BASE_URL = os.environ.get('PLUGIT_BASE_URL', '/')

PI_ALLOWED_NETWORKS = os.environ.get('PLUGIT_ALLOWED_NETWORKS', '0.0.0.0/0').split(',')

PI_API_NAME = 'plugit-sample'
