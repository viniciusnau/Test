from workasync.settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db_test.sqlite3",
    }
}
MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

ALLOWED_ORIGINS = ["*"]
DEBUG = True
