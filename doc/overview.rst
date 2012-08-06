.. _overview:

********
Overview
********

Brie is a re-implementation of the employee management system gorgonzola
and its associated confluence wiki, known as confluence. The goals of
brie are to modernize gorgonzola and fix its long-standing architectural
difficulties while retaining its unique capabilities for employee
management and scheduling.

Gorgonzola History
------------------
 
Gorgonzola dates back to at least 2002 and has been the only web
application which A&RT employees have used for work logistics since that
time. It is a collection of important applications for A&RT student
workers.

* Scheduler
* Planner
* Timeclock
* Employee discipline
* Employee management
* Job application submission

Detailed documentation of these components can be found in the
gorgonzola user specification hosted at the gorgonzola site, and
archived at <somewhere>. In addition to the above, gorgonzola is loosely
coupled with a confluence wiki known as conspace, which serves as a
knowledge base for the student employees.  The applications are
completely separate, although there are some surface-level efforts to
integrate them. For example, the gorgonzola clock-in button is located
on the conspace home page, and conspace contains links to gorgonzola.

Motivation for redesigning Gorgonzola
-------------------------------------

Gorgonzola is a PHP application which has been developed on-and-off
since its deployment in 2002. Features have been added to it over time
by many different people. Disorganization of gorgonzola's codebase and
frequent bugs prompted consideration of developing a replacement by
either finding a suitable existing package, or creating a new
application. After a survey of the available scheduling and employee
management packages used by other departments at Northwestern University
and elsewhere, the decision was made to redesign gorgonzola from
scratch.

Brie design philosophy
----------------------

One of the principle design goals of Brie was to be more organized and
robust than gorgonzola, making it easier for future development and
maintenance. For this reason, we elected to use `django
<http://www.djangoproject.com>`_, a web framework written in `python
<http://www.python.org>`_. Django can act as a CMS by use of the
`django-cms <http://www.django-cms.org>`_ project, but perhaps more
importantly, is a powerful web framework which provides us with a number
of tools to speed up development and improve organization of the
codebase. More details on django are provided in the detailed
implementation-level documentation.

Another major goal was improving the robustness of the project. A
substantial amount of effort has gone into writing programmatic tests
for ricotta, the part of Brie which has functionality similar to
gorgonzola. It is hoped that adequate testing will greatly reduce the
number of seemingly random bugs that were found in gorgonzola. For more
information, see the section of this documentation which focuses on
testing.

Lastly, Brie is not an exact rewrite of gorgonzola. The web has evolved
a great deal since 2002, and this project hopes to bring a great deal of
that evolution to the table. While Brie is not an incredibly
javascript-intensive application, javascript has been used to streamline
the user interface, especially in the calendar and planner
components. Surveys were also conducted of employees to determine which
features need to be reworked, and which features should be added. This
feedback was incorporated into the design process of Brie.
