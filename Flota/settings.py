"""
Django settings for Flota project.

Konfiguracja sterowana zmiennymi środowiskowymi, przygotowana pod deploy na
Vercel (Postgres + Cloudinary + WhiteNoise). Bez ustawionych zmiennych projekt
działa lokalnie na SQLite i lokalnym katalogu media/.
"""

from pathlib import Path
import os

import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Zmienne z pliku .env (tylko lokalnie). Na produkcji pochodzą z panelu Vercela.
load_dotenv(BASE_DIR / '.env')


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in ('1', 'true', 'yes', 'on')


# SECURITY -------------------------------------------------------------------
# Klucz produkcyjny ustaw w zmiennej SECRET_KEY. Domyślny jest TYLKO dla devu.
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-insecure-key-change-me')

DEBUG = env_bool('DEBUG', default=False)

# Hosty: z env (po przecinku) + lokalne + wszystkie subdomeny *.vercel.app.
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]
ALLOWED_HOSTS += ['localhost', '127.0.0.1', '.vercel.app']

# Vercel udostępnia bieżącą domenę deploymentu w tej zmiennej.
VERCEL_URL = os.environ.get('VERCEL_URL')
if VERCEL_URL:
    ALLOWED_HOSTS.append(VERCEL_URL)

# CSRF dla formularzy POST (login, kontakt itd.) zza HTTPS na Vercelu.
CSRF_TRUSTED_ORIGINS = ['https://*.vercel.app']
for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(','):
    origin = origin.strip()
    if origin:
        CSRF_TRUSTED_ORIGINS.append(origin)

# Vercel terminuje SSL na proxy – pozwól Django rozpoznać HTTPS.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Application definition ------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # cloudinary_storage musi być PRZED staticfiles (wymóg biblioteki).
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',

    'Pojazd',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise serwuje pliki statyczne (m.in. panel admina) na produkcji.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Flota.urls'
LOGIN_URL = '/login/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR, BASE_DIR / 'Flota' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Flota.wsgi.application'


# Database --------------------------------------------------------------------
# DATABASE_URL (Postgres na Vercel/Neon) jeśli ustawiony; inaczej lokalny SQLite.
_db_url = os.environ.get('DATABASE_URL', '')
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        # SSL wymuszamy tylko dla Postgresa (Neon/Vercel), nie dla SQLite.
        ssl_require=_db_url.startswith('postgres'),
    )
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'pl'
TIME_ZONE = 'Europe/Warsaw'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript) ---------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT_DIR') or (BASE_DIR / 'staticfiles')
STATICFILES_STORAGE = os.environ.get(
    'STATICFILES_STORAGE',
    'whitenoise.storage.CompressedStaticFilesStorage',
)
# WhiteNoise serwuje statyki (panel admina) wprost z finderów aplikacji —
# bez potrzeby uruchamiania collectstatic w buildzie na Vercelu.
WHITENOISE_USE_FINDERS = True


# Media files (uploady) -------------------------------------------------------
# Produkcja: Cloudinary (Vercel ma system plików read-only i ulotny).
# Lokalnie (bez CLOUDINARY_URL): domyślny storage do katalogu media/.
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
if os.environ.get('CLOUDINARY_URL'):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


# Email (formularz kontaktowy) ------------------------------------------------
# Bez konfiguracji SMTP maile lądują w konsoli (dev). Na produkcji ustaw
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend i dane EMAIL_*.
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '465'))
EMAIL_USE_SSL = env_bool('EMAIL_USE_SSL', default=True)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
CONTACT_RECIPIENT = os.environ.get('CONTACT_RECIPIENT', EMAIL_HOST_USER)


# Zachowaj dotychczasowe AutoField, by nie generować zbędnych migracji.
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
