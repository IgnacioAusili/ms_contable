from ms_contable.settings import *

ALLOWED_HOSTS = [*ALLOWED_HOSTS, "mscontable"]
CSRF_TRUSTED_ORIGINS = ["https://mscontable"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
