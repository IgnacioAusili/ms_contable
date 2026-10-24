import os
import time
from pathlib import Path

from django.core.management.utils import get_random_secret_key

from ms_contable.settings import *


def _load_or_create_secret_key(path):
    path.parent.mkdir(parents=True, exist_ok=True)

    for _ in range(100):
        try:
            descriptor = os.open(
                path,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
            )
        except FileExistsError:
            secret_key = path.read_text(encoding="ascii").strip()
            if secret_key:
                return secret_key
            time.sleep(0.02)
            continue

        secret_key = get_random_secret_key()
        try:
            with os.fdopen(
                descriptor,
                "w",
                encoding="ascii",
                newline="\n",
            ) as secret_file:
                secret_file.write(secret_key + "\n")
                secret_file.flush()
                os.fsync(secret_file.fileno())
        except Exception:
            path.unlink(missing_ok=True)
            raise
        return secret_key

    raise RuntimeError(f"No se pudo leer o crear la clave de Django: {path}")


SECRET_KEY = _load_or_create_secret_key(
    DATA_DIR.parent / "config" / "django-secret-key"
)

ALLOWED_HOSTS = [*ALLOWED_HOSTS, "mscontable"]
CSRF_TRUSTED_ORIGINS = ["https://mscontable"]
SESSION_HEARTBEAT_TOKEN = os.environ.get("MSCONTABLE_SESSION_TOKEN", "")
SESSION_HEARTBEAT_DIR = Path(
    os.environ.get("MSCONTABLE_HEARTBEAT_DIR", DATA_DIR / "browser-sessions")
).expanduser()
https_port = os.environ.get("MSCONTABLE_HTTPS_PORT", "")
if https_port.isdecimal() and 1 <= int(https_port) <= 65535:
    CSRF_TRUSTED_ORIGINS.append(f"https://mscontable:{int(https_port)}")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
