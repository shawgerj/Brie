.. _deployment:

*****************
Server Deployment
*****************

This document covers the difference in configuration between running django on its included development server and sqlite3, and running it under apache using ``mod_wsgi`` and MySQL. The latter method is the preferred method of deployment, while the former makes for fast and easy development.

Django Development Server
=========================

Running Django with Apache
==========================

In this section, I describe the current setup of the development server at `<http://devconspace.at.northwestern.edu>`_. It is a "first crack" at setting up Django with ``mod_wsgi`` and MySQL. This configuration will probably need to change over time.

virtualenv
----------
The official documentation for Python virtualenv can be found at `<http://www.virtualenv.org/>`_. The idea is that we can set up all our Python libraries locally, without root-level permissions for the server. Additionally, each virtualenv is a self-contained entity, so we will not stomp on any other Python installations on the server by installing our own versions of our libraries. Follow the instructions on the virtualenv site to set it up.

One note: once virtualenv, you will want to run things with the python executable found in virtualenv, not the system-level python, because ``/usr/bin/python`` will not have access to any of your installed libraries! So, assuming virtualenv is set up in ``~/venv``, use ``~/venv/bin/python``. You can add ``~/venv/bin`` to your path by running ``PATH=$PATH:/home/<user>/venv/bin``.

``httpd.conf``
--------------
Firstly, make sure that ``mod_wsgi`` is installed, and loaded into Apache with ``LoadModule wsgi_module modules/mod_wsgi.so``. There are some detailed tutorials for how to set this up in the django and ``mod_wsgi`` documentation [#f1]_, [#f2]_. Here are the lines which have been added to ``/etc/httpd/conf/httpd.conf``.::

    WSGIScriptAlias /wsgi-app /home/jms511/Brie/apache/django.wsgi
    WSGIPythonPath /home/jms511/venv/lib/python2.7/site-packages
    WSGIPassAuthorization On

    Alias /static/ /home/jms511/Brie/ricotta/static/

    <Directory /home/jms511/Brie/ricotta/static>
        Order allow,deny
        Allow from all
    </Directory>

    <Directory /home/jms511/Brie/apache>
        Order allow,deny
        Allow from all
    </Directory>

``WSGIScriptAlias`` will need to change depending on where the Django app is located. The first argument is the URL-path, so in this example, we will be able to find our app at `<http://devconspace.at.northwestern.edu/wsgi-app>`_. The second argument specifies where to find the app. We always want to be pointing at the ``django.wsgi`` file in our project.

Because this project uses Python virtualenv instead of globally installed python packages, we need to set ``WSGIPythonPath`` to the ``site-packages`` directory inside the virtual environment.

``WSGIPassAuthorization`` is for django-tastypie. For some reason, ``mod_wsgi`` will strip out the authorization headers, resulting in a whole bunch of HTTP 401 FORBIDDEN errors when accessing the tastypie API unless this variable is turned on.

MySQL
-----
Django makes it really easy to switch from sqlite3 to MySQL, because all the database-specific operations are abstracted away. Just change your ``settings.py`` file.::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'devconspace',
            'USER': 'devconspace',
            'PASSWORD': 'password',
            'HOST': 'bion.at.northwestern.edu',
            'PORT': '' # set to empty string for default
        }
    }

.. rubric:: Footnotes
.. [#f1] `WSGI integration with Django <http://code.google.com/p/modwsgi/wiki/IntegrationWithDjango>`_
.. [#f2] `How to use Django with Apache and mod_wsgi <https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/modwsgi/>`_
