.. _deployment:

*****************
Server Deployment
*****************

This document covers the difference in configuration between running django on its included development server and sqlite3, and running it under apache using ``mod_wsgi`` and MySQL. The latter method is the preferred method of deployment, while the former makes for fast and easy development.

Git
===
For lack of a better place, the details on git hosting are being included here. This project is hosted on `github <www.github.com>`_ at `<https://www.github.com/shawgerj/Brie>`_. Github and the git documentation have many more details on how to do manage git projects than I will put here. Github in particular says how to set up your computer for use with the (highly convenient) github service [#f1]_, [#f2]_. 

.. attention::
    This next section might be speculative in the case that I don't have time to implement separate development and production branches tonight or tomorrow. In that case, add it to the wishlist and adjust this notice as necessary.

Branches
--------
There are two important branches in the git repository, development and production. The only differences between these two branches should be in ``settings.py``, in the ``DATABASES`` section. We want to be using sqlite3 for the development branch, and MySQL for the production branch. Switching between the development server and apache requires no changes in the app.

The github repository is public, so it is best not to put sensitive information there. Since the database is stored outside the git repository -- or at least it should be; please do not add brie.db to the repository --, this is not a big issue. For the production branch, keep the database login information in a separate file which is not managed by the repository.

Django Development Server
=========================
To run the django development server, run ``python manage.py runserver``. It is tied to ``localhost:8000``, so point your browser to ``http://localhost:8000`` to see the site. The development server is a highly convenient way to use and test the project, but it is not recommended for use in production environments. 

Handy tip for working remotely: The development server is only visible from localhost, so your site will not be visible from any other computers unless you use ssh and forward port 8000.

Running Django with Apache
==========================

In this section, I describe the current setup of the development server at `<http://devconspace.at.northwestern.edu>`_. It is a "first crack" at setting up Django with ``mod_wsgi`` and MySQL. This configuration will probably need to change over time.

virtualenv
----------
The official documentation for Python virtualenv can be found at `<http://www.virtualenv.org/>`_. The idea is that we can set up all our Python libraries locally, without root-level permissions for the server. Additionally, each virtualenv is a self-contained entity, so we will not stomp on any other Python installations on the server by installing our own versions of our libraries. Follow the instructions on the virtualenv site to set it up.

One note: once virtualenv, you will want to run things with the python executable found in virtualenv, not the system-level python, because ``/usr/bin/python`` will not have access to any of your installed libraries! So, assuming virtualenv is set up in ``~/venv``, use ``~/venv/bin/python``. You can add ``~/venv/bin`` to your path by running ``PATH=$PATH:/home/<user>/venv/bin``.

``httpd.conf``
--------------
Firstly, make sure that ``mod_wsgi`` is installed, and loaded into Apache with ``LoadModule wsgi_module modules/mod_wsgi.so``. There are some detailed tutorials for how to set this up in the django and ``mod_wsgi`` documentation [#f3]_, [#f4]_. Here are the lines which have been added to ``/etc/httpd/conf/httpd.conf``.::

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
.. [#f1] `Set Up Git <https://help.github.com/articles/set-up-git>`_
.. [#f2] `Git Documentation <http://git-scm.com/documentation>`_
.. [#f3] `WSGI integration with Django <http://code.google.com/p/modwsgi/wiki/IntegrationWithDjango>`_
.. [#f4] `How to use Django with Apache and mod_wsgi <https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/modwsgi/>`_
