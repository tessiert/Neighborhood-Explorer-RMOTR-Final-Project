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
