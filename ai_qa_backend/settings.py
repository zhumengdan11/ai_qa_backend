import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-default-key-change-in-production')
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,.railway.app,*.up.railway.app').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'qa_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'ai_qa_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.csrf',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ai_qa_backend.wsgi.application'

# 数据库配置 - Railway MySQL / MySQL直连 / SQLite本地开发
# Railway 会自动注入 MYSQL_* 或 DATABASE_URL 环境变量
import re
DATABASE_URL = os.getenv('DATABASE_URL', '')
RAILWAY_ENV = os.getenv('RAILWAY_SERVICE_ID', '') != ''

if RAILWAY_ENV or os.getenv('USE_MYSQL', '') == 'True':
    if DATABASE_URL and DATABASE_URL.startswith('mysql://'):
        # Railway DATABASE_URL 格式: mysql://user:pass@host:port/dbname
        m = re.match(r'mysql://([^:]+):([^@]+)@([^:]+):(\\d+)/(.+)', DATABASE_URL)
        if m:
            db_user, db_pass, db_host, db_port, db_name = m.groups()
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.mysql',
                    'NAME': db_name,
                    'USER': db_user,
                    'PASSWORD': db_pass,
                    'HOST': db_host,
                    'PORT': db_port,
                    'OPTIONS': {'charset': 'utf8mb4'},
                }
            }
        else:
            DATABASES = {'default': {'ENGINE': 'django.db.backends.mysql', 'NAME': '', 'USER': '', 'PASSWORD': '', 'HOST': '', 'PORT': ''}}
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': os.getenv('MYSQL_DATABASE', 'ai_qa_db'),
                'USER': os.getenv('MYSQL_USER', 'root'),
                'PASSWORD': os.getenv('MYSQL_PASSWORD', ''),
                'HOST': os.getenv('MYSQL_HOST', 'localhost'),
                'PORT': os.getenv('MYSQL_PORT', '3306'),
                'OPTIONS': {'charset': 'utf8mb4'},
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===== Railway / 生产环境安全配置 =====
RAILWAY_ENV = os.getenv('RAILWAY_SERVICE_ID', '') != ''

if RAILWAY_ENV or not DEBUG:
    # HTTPS 安全
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # CSRF 信任域名
    RAILWAY_PUBLIC_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN', '')
    if RAILWAY_PUBLIC_DOMAIN:
        CSRF_TRUSTED_ORIGINS = [f'https://{RAILWAY_PUBLIC_DOMAIN}']
    
    # 静态文件压缩与缓存
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # 关闭 DEBUG
    DEBUG = False

# SESSION 配置
SESSION_COOKIE_AGE = 60 * 60 * 24  # 24小时
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

SESSION_COOKIE_AGE = 60 * 60 * 24
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

QWEN3_API_KEY = os.getenv('QWEN3_API_KEY', '')
QWEN3_BASE_URL = os.getenv('QWEN3_BASE_URL', 'https://api.qwen.ai/v1')
QWEN3_MODEL = os.getenv('QWEN3_MODEL', 'qwen3-7b')

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@school.edu.cn')
