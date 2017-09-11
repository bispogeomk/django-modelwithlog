from distutils.core import Command
from setuptools import setup


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from django.conf import settings
        settings.configure(
            DATABASES={'default': {'NAME': ':memory:', 'ENGINE': 'django.db.backends.sqlite3'}},
            INSTALLED_APPS=(
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'log_models',
                'log_models.model_test',
                'jsonfield',
                'django_extensions')
        )
        from django.core.management import call_command
        import django

        if django.VERSION[:2] >= (1, 7):
            django.setup()
        
        # call_command('shell_plus')
        call_command('makemigrations')
        call_command('migrate')
        call_command('test', 'log_models')
        

setup(
    name='django-modelwithlog',
    version='0.9.0',
    packages=['django-jsonfield'],
    license='MIT',
    include_package_data=True,
    author='Bispo',
    author_email='bispo@geomk.com.br',
    url='https://github.com/bispogeomk/ModelWithLog/',
    description='A reusable Django Model that allows you to store registre actions log of models.',
    long_description=open("README.rst").read(),
    install_requires=['Django >= 1.8.0'],
    tests_require=['Django >= 1.8.0'],
    cmdclass={'test': TestCommand},
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
    ],
)
