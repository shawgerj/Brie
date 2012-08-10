.. _testing:

*******
Testing
*******

Testing is a great way to ensure program robustness, because it converts opinions about how a program works into verifiable facts. Assuming the set of tests is complete, they can also warn developers of regression bugs - the tests can be re-run whenever any changes are made, and failed tests will instantly point to the source of a problem. Lastly, tests provide up-to-date documentation and examples of how to use the application. At this time we test three main areas of ricotta -- API, models, and views. Other tests, such as form tests, maybe be required in the future, but these are workable for now.

Test Fixtures
=============
Originally, the ricotta tests ran off a large set of fixtures which contained a great deal of initial state. The fixtures set up examples of each model, which would then be tested. Unfortunately, fixtures are a bad idea for a number of reasons.

* Code bloat. The fixture file grew to over 5000 lines.
* Maintainability. Fixtures must be regenerated every time the schema changes.
* Key problems. Permissions and contenttypes do not work well in fixtures, and there are key overlap problems.
* Improper isolation. Loading a large state for each test meant that tests could potentially be depending on state which they should not be.

Note that there is still a ricotta fixture called ``initial_data.yaml`` which contains initial location data. As this data is unlikely to change often, it is a convenient and mostly-harmless use of a fixture.

Test Factories
==============
To avoid using fixtures, the tests were re-written using `factory_boy <http://github.com/rbarrois/factory_boy>`_, a library for writing factories [#f1]_. Instead of defining a lot of state in a fixtures file, the state is dynamically created by harnessing factories to generate the objects needed for tests. 

Here is an example of a factory which makes ``Shift`` objects.::

    class ShiftFactory(factory.Factory):
        FACTORY_FOR = Shift

	for_trade = False
	been_traded = False
	start_time = timezone.now()
	end_time = timezone.now() + datetime.timedelta(hours=1)

``FACTORY_FOR`` always specifies the name of the model. Underneath that are the default values for some of the model fields. Defaults can be overwritten by setting them when calling the factory. Also, we left ``location_name`` and ``worker`` out. These fields will have to be defined when we use the factory. Here is how to make a ``Shift`` using this factory.::

    # ConsultantFactory is another factory defined in factories.py
    consultant = ConsultantFactory()
    tech_lab = Location.objects.get(location_name='Tech')

    shift = ShiftFactory(worker = consultant.user, location_name = tech_lab)

Factories can be built or created. Building a factory merely creates it in memory, while creating a factory writes it to the database. You can control this behavior by using the member functions ``.build()`` or ``.create()``. In ricotta, factories have been set to build by default, so the above example builds a consultant worker and a shift. If we wanted to write the shift to the database, we could do this instead.::

    shift = ShiftFactory.create(worker = consultant.user, location_name = tech_lab)

In general, it is better to avoid writing to the database during tests because it is much slower than handling everything in memory. 


Tests
=====

Currently, there are three types of tests in ricotta -- model, view, and API tests. An example of each is given here.

Model Tests
-----------

These tests, found in ``tests/model_tests.py``, test the models in ``models.py``. The general pattern of these tests is to create an object via a factory, then test a few of its basic properties.::

    class DisciplineRecordTestCase(TestCase):
        def test_disciplinerecord(self):
            consultant = ConsultantFactory()
	    conleader = COnleaderFactory()
	    d1 = DisciplineRecordFactory(
	        employee = consultant.user, changed_by = conleader.user)

            self.assertEquals(d1.employee.username, 'testcon')
            self.assertEquals(d1.changed_by.username, 'testcl')

In this example, a consultant and a conleader user were built. They were then used to build a new ``DisciplineRecord``. At the end, we check that consultant is stored in the ``employee`` attribute of ``d1``, and the conleader is stored in the ``changed_by`` attribute.

All of the model tests inherit from ``django.test.TestCase`` [#f2]_.

View Tests
----------

The view tests can be found in ``tests/view_tests.py``. In these tests, we set up a client (see `django.test.client.Client <https://docs.djangoproject.com/en/1.4/topics/testing/#module-django.test.client>`_), use it to request a URL, and then test for a ``status_code`` and for whatever should be in the ``resp.context``. This isn't the only way of testing views, and there are probably much better and more focused ways of approaching it. See this interesting `video <pyvideo.org/video/699/testing-and-django>`_ for a more detailed discussion.::

    class TimeclockViewsTestCase(TestCase):
        def setUp(self):
	    self.con = ConsultantFactory.create().user
            TimeclockRecordFactory.create(employee=self.con)
            self.client.login(username=self.con.username, password='testcon')

        def test_timeclock_view(self):
            resp = self.client.get('/ricotta/timeclock/testcon/')
            self.assertEqual(resp.status_code, 200)
            self.assertTrue('tr_data' in resp.context)
	    self.assertEqual(resp.context[-1]['tr_data'].count(), 1)

A couple things to note: we are using the ``create()`` method because the ``User`` and ``TimeclockRecord`` objects won't exist in our view if we do not save them to the database first. Also, ``self.client.login()`` is how we log in users to the client. In this instance, we log in a user in the consultant group, but if we were to log in a user in the conleader group, they would have different permissions.

All of the view tests inherit from ``django.test.TestCase`` [#f2]_.

API Tests
---------

These tests, found in ``tests/api_tests.py``, test the django-tastypie API we have set up for use with the calendar and planner components of ricotta. More information on exactly how the API works is documented elsewhere. Here is an abbreviated test.::

    class LocationResourceTest(ResourceTestCase):
        def setUp(self):
            super(LocationResourceTest, self).setUp()

            self.testcl = ConleaderFactory.create().user
            self.testcon = ConsultantFactory.create().user
        
        def get_normal_credentials(self):
            return self.create_apikey(username=self.testcon.username, 
                                  api_key=self.testcon.api_key.key)
        def get_admin_credentials(self):
            return self.create_apikey(username=self.testcl.username,
                                  api_key=self.testcl.api_key.key)
        
        def test_get_list_json(self):
            resp = self.api_client.get('/api/v1/location/', format='json')
            self.assertValidJSONResponse(resp)
            self.assertEqual(len(self.deserialize(resp)['objects']), 6)
        
            # might as well test if user permissions work, although we don't 
            # actually need them
            resp = self.api_client.get('/api/v1/location/', format='json', 
                                       authentication=self.get_normal_credentials())
            self.assertValidJSONResponse(resp)
            resp = self.api_client.get('/api/v1/location/', format='json', 
                                       authentication=self.get_admin_credentials())
            self.assertValidJSONResponse(resp)

These tests require more setup than the other ones we have looked at so far. They make use of the ``setUp`` function, which sets the state before the actual tests are run. The API authentication procedure is different than one we used on views. ``get_normal_credentials()`` and ``get_admin_credentials()`` are helper functions to get users' ``api_key``. This is explained in more detail in the django-tastypie documentation, and the motivation for it is explained in the calendar section of this document.

These tests inherit from ``tastypie.test.ResourceTestCase``, which defines some assertion methods which are specific to tastypie APIs. It builds on top of ``django.test.TestCase``.

.. rubric:: Footnotes

.. [#f1] `factory_boy official documentation <http://factoryboy.readthedocs.org/en/latest/>`_
.. [#f2] `django.test.TestCase <https://docs.djangoproject.com/en/1.4/topics/testing/#django.test.TestCase>`_
