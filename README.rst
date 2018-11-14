Neighborhood Explorer
=====================

A web app to explore key features of U.S. neighborhoods

This site is currently under active development, and represents my final project
for the RMOTR "Web Development with Python and Django" 
program.  The current state of the project can be accessed at
https://neighborhood-explorer.herokuapp.com.  It enables a user to enter some or all of a U.S. address, and then 
retrieves and displays information about the given location - a three-day 
weather forecast and a map and drop-down selection mechanism for the exploration 
of attractions and other points of interest in the area.  

I start by using Mapquest's geocoding API to convert the input location into latitude and 
longitude coordinates, and then use these to pull weather information from the 
Dark Sky weather API.  After that, and based on user selection criteria, I pull points of interest information from the 
Mapquest Place Search API and use this information to populate an appropriately scaled map from the
Mapquest Static Map API with location markers, as well as to retrieve and display
associated textual information.

This site also provides its own API endpoint at 
http://Neighborhood-Explorer.herokuapp.com/api/
which allows GET requests,
and will return JSON containing information on how many times each City/State
combination in the database (PostgreSQL is used) has been searched.  It is this 
API that is accessed by the home page in order to construct the "Top Searches"
results - employing a very simple in-house microservices architecture approach.

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django


:License: MIT


Settings
--------

Moved to settings_.

.. _settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html

Basic Commands
--------------

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

Type checks
^^^^^^^^^^^

Running type checks with mypy:

::

  $ mypy neighborhood_explorer

Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ pytest

Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moved to `Live reloading and SASS compilation`_.

.. _`Live reloading and SASS compilation`: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html





Deployment
----------

The following details how to deploy this application.


Heroku
^^^^^^

See detailed `cookiecutter-django Heroku documentation`_.

.. _`cookiecutter-django Heroku documentation`: http://cookiecutter-django.readthedocs.io/en/latest/deployment-on-heroku.html




