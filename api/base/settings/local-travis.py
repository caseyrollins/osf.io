from .defaults import *  # noqa


# DATABASES = {
#     'default': {
#         'CONN_MAX_AGE': 0,
#         'ENGINE': 'osf.db.backends.postgresql',  # django.db.backends.postgresql
#         'NAME': os.environ.get('OSF_DB_NAME', 'osf'),
#         'USER': os.environ.get('OSF_DB_USER', 'postgres'),
#         'PASSWORD': os.environ.get('OSF_DB_PASSWORD', ''),
#         'HOST': os.environ.get('OSF_DB_HOST', '127.0.0.1'),
#         'PORT': os.environ.get('OSF_DB_PORT', '54321'),
#         'ATOMIC_REQUESTS': True,
#     }
# }

VARNISH_SERVERS = ['http://127.0.0.1:8080']
ENABLE_VARNISH = True
ENABLE_ESI = False

REST_FRAMEWORK['ALLOWED_VERSIONS'] = (
    '2.0',
    '2.0.1',
    '2.1',
    '2.2',
    '2.3',
    '3.0',
    '3.0.1',
)
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'user': '1000000/second',
    'non-cookie-auth': '1000000/second',
    'add-contributor': '1000000/second',
    'create-guid': '1000000/second',
    'root-anon-throttle': '1000000/second',
    'test-user': '2/hour',
    'test-anon': '1/hour',
}

ALLOWED_HOSTS.append('localhost')
