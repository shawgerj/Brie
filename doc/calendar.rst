.. _calendar:

********
Calendar
******** 
The calendar is, so far, the most complex portion of ricotta. It has several different components which work together to make it work. They are outlined here.

Usage
=====
Conceptually, the calendar is pretty simple. There is one calendar per location, and it contains the shifts which employees are scheduled to work. Shifts are displayed much like on a google calendar -- the shift is represented as a block with the employee's name on it. 

Conleader Actions
-----------------
Conleaders are in charge of the actual scheduling -- normal users cannot modify shifts. Conleaders may create or delete shifts and assign any consultant to a shift. They may also change the start/end times or assignment of shifts which are already created. They may put any shift up for trade, and reset any shift which is up for trade to normal status.

Consultant Actions
------------------
Consultants may put their own shifts up for trade and take shifts which other have put up for trade. They have no other modification powers. 

The Shift Model
===============
Calendars manipulate Shift models. Here is the definition::

    class Shift(models.Model):
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	location_name = models.ForeignKey(Location)
	worker = models.ForeignKey(User, null=True)
	for_trade = models.BooleanField()
	been_traded = models.BooleanField()

This is pretty much as-expected. Note that ``location_name`` and ``worker`` are both ForeignKey fields. 

django-tastypie
===============
Because FullCalendar.js uses a REST API [#f1]_ to talk to webservices, we would like some way of doing that with Django. Django-tastypie [#f2]_ lets us create an API of this nature which interacts with our django models. All the code for this is in ``ricotta/api.py``. 

Available APIs
--------------
Here the APIs which are defined in ``ricotta/api.py``.

.. csv-table::
    :header: "API Name", "Allowed Operations", "Authenticated"

    "``/api/v1/user/``", "GET", "No"
    "``/api/v1/location/``", "GET", "No"
    "``/api/v1/shift/``", "GET, POST, PATCH, DELETE, PUT", "Yes"
    "``/api/v1/planner_block/``", "GET, POST, PATCH, DELETE, PUT", "Yes"



API Authentication
------------------
We don't want just anybody connecting to the API and mucking up our shifts by accident or on purpose, so the parts of the API which permit modification are protected by authentication. Tastypie has several options for this, but we use ApiKey authentication. Each user has an associated ApiKey which is created by a ``post_save`` hook upon the user's creation. When we send an API request, the username and ApiKey associated with that user must be sent along with it. The script ``backbone-tastypie.js`` makes this easy to do with ``backbone.js``, as it overloads ``Backbone.sync`` and gives us somewhere to put that extra authentication information.

We need to add an extra bit of javascript after including ``backbone-tastypie.js``.::

    Backbone.Tastypie.apiKey = {
        username: 'username',
        key: '1ee7b199fce22f7c8641976300063cf11e80250a'

From then on, all the REST requests which come through backbone.js will have this extra authentication information included

``backbone.js``
===============
This is an interesting javascript library which helps us organize shifts into data structures for use with FullCalendar. Backbone.js has two main data structures -- models, and collections, which are just groups of models. In our case, events can be represented as models, and all the events which we have requested are a collection.

.. Attention::
    This is an important note for future work. Right now, the calendar just blindly requests all the shifts from a certain location and displays them on the calendar. This could become wasteful of resources as more and more shifts start being stored. It would be best to only retrieve a couple weeks of shifts, and then dynamically load more if the user chose to view further back or forward in time.

The code which interacts with ``backbone.js`` is in ``/static/js/application.js``. The models and collections are defined at the top. Backbone.js only needs the URL to our django-tastypie API, and it makes it pretty easy to create collections. EventsView() and EventView() are the functions where the action of displaying the calendar and its UI take place. EventsView displays the entire calendar in the render function. Most of its other functions delegate to EventView or FullCalendar. EventView is what gets called when a user clicks on a shift. It is responsible for the pop-up dialog, and controlling the actions of the buttons on that dialog.

I followed several tutorials to integrate tastypie, backbone, and FullCalendar. They are included here for reference. 

* `Building a shared calendar with Backbone.js and FullCalendar <http://blog.shinetech.com/2011/08/05/building-a-shared-calendar-with-backbone-js-and-fullcalendar-a-step-by-step-tutorial/>`_
* `Integration of Backbone.js with Tastypie <http://paltman.com/2012/04/30/integration-backbonejs-tastypie/>`_
* `Backbone.js and Django <http://joshbohde.com/blog/backbonejs-and-django>`_

FullCalendar
============
`FullCalendar <http://arshaw.com/fullcalendar/>`_ is a really handy `jQuery <http://www.jquery.org>`_ plugin that displays events much like a google calendar. In fact, you can even configure it to display events from google calendar, but that is not how we are using it. All the initialization settings for FullCalendar can be found in ``/static/js/application.js``. We disable the month and agenda views -- we only want to show one week at a time. 

.. Attention::
    When all the user permissions are actually implemented, FullCalendar should behave a little differently for consultants than for conleaders. Consultants should not be able to drag shifts around or change their start or end times. Ideally this will be enforced on the API backend as well, but it should not be possible on the frontend either. 

Future Work
===========

.. rubric:: Footnotes

.. [#f1] `Representational state transfer <http://en.wikipedia.org/wiki/Representational_state_transfer>`_
.. [#f2] `django-tastypie <http://github.com/toastdriven/django-tastypie>`_

