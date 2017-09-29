django-modelwithlog
-------------------

django-modelwithlog is a reusable Django Abstract Model that make automatic history log of your model.

The History of all model will write in a Model RegisterLog compose of:

    action_time:
        date and time of ocurrency

    content_type:
        The ContentType of the concrect Model

    data_user:
        A JSON of user and acess data loged on ocurrency

    modifications:
        A JSON with a data of model modificate

    object_pk:
        The primary key of model

    object_repr:
        The representation of model

    action_flag:
        The action of ocurrency (ADDITION, CHANGE or DELETION)

    change_message:
        The message of ocurrency of human read

Setup/Usage
===========

.. code-block:: shell

    pip install django-modelwithlog

or

.. code-block:: shell

    pip install git+https://github.com/bispogeomk/django-modelwithlog


Add `threadlocals.middleware.ThreadLocalMiddleware` to your `MIDDLEWARE_CLASSES` setting.

Add 'log_models' to your 'SETTINGS.INSTALLED_APPS'.

Inherit your model from 'ModelWithLog' to make it auto logged:

.. code-block:: python

    from django.db import models
    from log_models import ModelWithLog

    class MyModel(ModelWithLog):
        name = models.CharField(max_length=80)
        age = models.PositiveSmallIntegerField()

Advanced Usage
--------------

.. code-block:: python

    from django.db import models
    from log_models.models import ModelWithLog
    from log_models.models import RegisterLog
    from django.contrib.contenttypes.models import ContentType

    class Player(ModelWithLog):
        name = models.CharField(max_length=80)
        age = models.PositiveSmallIntegerField()

        def make_log_message(self):
            self.full_clean()
            if self.__action_flag__ == 1:
                return f"A new Player nome {self.nome} with age {self.age}."
            elif self.__action_flag__ == 3:
                return f"Player {self.nome} is gone."
            else:
                return f"The Player change for {self.nome} and age {self.age}."

        def get_logs(self):
            return RegisterLog.objects.filter(content_type=ContentType(Player), object_pk=self.pk)

Compatibility
--------------

django-modelwithlog aims to support the same versions of Django currently maintained by the main Django project. See `Django supported versions`_, currently:

  * Django 1.10 with Python 3.5
  * Django 1.11 (LTS) with Python 3.5 or 3.6


Testing django-modelwithlog Locally
--------------------------------

To test against all supported versions of Django:

.. code-block:: shell

    $ python setup.py test


Contact
-------
Web: http://www.snaketi.com.br

Twitter: `@moacirbispo`_

Email: `bispo@geomk.com.br`_

.. _bispo@geomk.com.br: mailto:bispo@geomk.com.br
.. _@moacirbispo: https://twitter.com/moacirbispo

Changes
-------

Take a look at the `changelog`_.

.. _changelog: https://github.com/bispogeomk/django-modelwithlog/blob/master/CHANGES.rst