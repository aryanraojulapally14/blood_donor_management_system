
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'secret'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
'core'
]

MIDDLEWARE = [
'django.middleware.security.SecurityMiddleware',
'django.contrib.sessions.middleware.SessionMiddleware',
'django.middleware.common.CommonMiddleware',
'django.middleware.csrf.CsrfViewMiddleware',
'django.contrib.auth.middleware.AuthenticationMiddleware',
'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'blood_donor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',   # ✅ IMPORTANT
                'django.contrib.auth.context_processors.auth',  # ✅ REQUIRED
                'django.contrib.messages.context_processors.messages', 
                'core.context_processors.user_role', # ✅ REQUIRED
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',   # ✅ IMPORTANT LINE
    }
}

STATIC_URL = '/static/'

# Email config (edit before use)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'lifelink.donations@gmail.com'
EMAIL_HOST_PASSWORD = 'vfey aliz adyw vujr'

# 🔥 TIMEZONE FIX
TIME_ZONE = 'Asia/Kolkata'
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


