import os
basedir = basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

BASIC_AUTH_USERNAME = 'YOUR_USERNAME_HERE'
BASIC_AUTH_PASSWORD = 'YOUR_PASSWORD_HERE'