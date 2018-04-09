from distutils.core import Command
from setuptools import setup


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass
    
    def fake_json(self):
        return [{'teste': 1}, {'item': 2}, 5, 4, '6']

    def run(self):
        from django.conf import settings
        settings.configure(
            DATABASES={'default': {'NAME': ':memory:',
                                   'ENGINE': 'django.db.backends.sqlite3'}},
            INSTALLED_APPS=(
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'log_models',
                'log_models.model_test',
                'jsonfield'),
            MIDDLEWARE=[
                'django.middleware.security.SecurityMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
                'threadlocals.middleware.ThreadLocalMiddleware',
            ],
            MOMMY_CUSTOM_FIELDS_GEN = {
                'jsonfield.fields.JSONField': self.fake_json,
            }
        )
        import django
        django.setup()
        from django.core.management import call_command
        call_command('makemigrations')
        call_command('migrate')
        call_command('test', 'log_models')


class ShellCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from django.conf import settings
        settings.configure(
            DATABASES={'default': {'NAME': ':memory:',
                                   'ENGINE': 'django.db.backends.sqlite3'}},
            INSTALLED_APPS=(
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'log_models',
                'log_models.model_test',
                'jsonfield',
                'django_extensions'),
            MIDDLEWARE=[
                'django.middleware.security.SecurityMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
                'threadlocals.middleware.ThreadLocalMiddleware',
            ]
        )
        import django
        django.setup()
        from django.core.management import call_command
        call_command('makemigrations')
        call_command('migrate')
        call_command('shell_plus')



setup(
    name='django-modelwithlog',
    version='1.0.1',
    packages=['log_models', 'log_models.migrations'],
    license='MIT',
    include_package_data=True,
    author='Bispo',
    author_email='bispo@geomk.com.br',
    url='https://github.com/bispogeomk/django-modelwithlog/',
    description=('A reusable Django Model that allows you to store'
                 'registre actions log of models.'),
    long_description=open("README.rst").read(),
    install_requires=['Django >= 1.8.0', 'jsonfield', 'django-threadlocals'],
    tests_require=['Django >= 1.8.0', 'jsonfield', 'django-threadlocals', 'model_mommy',
                   'mock', 'django_extensions', 'jsonfield'],
    cmdclass={'test': TestCommand, 'shell': ShellCommand},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: System :: Logging',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
    ],
)
