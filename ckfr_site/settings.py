import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only")
DEBUG = os.getenv("RENDER") is None

# --- HOSTS ---
if DEBUG:
    # Local dev & GitHub Codespaces
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".app.github.dev"]
else:
    # Render + your domains
    ALLOWED_HOSTS = [
        os.getenv("RENDER_EXTERNAL_HOSTNAME", ""),
        "ckfr.fr", "www.ckfr.fr",
    ]

# --- CSRF trusted origins (schemes required) ---
CSRF_TRUSTED_ORIGINS = [
    # Dev (local & Codespaces)
    "http://localhost:8000",
    "https://localhost:8000",
    "http://127.0.0.1:8000",
    "https://127.0.0.1:8000",
    "https://*.app.github.dev",      # Codespaces
    # Prod (Render + your domains)
    "https://*.onrender.com",
    "https://ckfr.fr",
    "https://www.ckfr.fr",
]

INSTALLED_APPS = [
    "ckfr_site.apps.CkfrSiteConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ops",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ckfr_site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "ops.context_processors.permissions_flags",
            ],
        },
    }
]

WSGI_APPLICATION = "ckfr_site.wsgi.application"

# DB: SQLite locally, Postgres on Render via DATABASE_URL
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR/'db.sqlite3'}",
        conn_max_age=600, ssl_require=False
    )
}

# Static files (WhiteNoise)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }
}

# Auth redirects
LOGIN_URL = "/"
if DEBUG:
    LOGIN_REDIRECT_URL = "/operation/"
else:
    LOGIN_REDIRECT_URL = "https://www.ckfr.fr/operation/"
    
# Security (prod only)
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 3600 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# Strong password hashing
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

# --- Locale (French) ---
LANGUAGE_CODE = "fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

LOGOUT_REDIRECT_URL = "/"