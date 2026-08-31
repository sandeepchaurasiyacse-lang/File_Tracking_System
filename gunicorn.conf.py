import os

bind = '0.0.0.0:' + os.environ.get('PORT', '10000')
wsgi_app = 'fms.wsgi:application'
workers = 2
timeout = 120
