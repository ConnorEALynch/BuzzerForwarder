# BuzzerForwarder
## Introduction
Many apartments have deprecated lobby door authorization designed to route to a single home phone. in modern times the home phone is extinct replaced with the personal mobile phone. This software operates as a “man-in the-middle” to simultaneous ring the tenant’s phones, connect the first to pickup, allow them to converse and enter the code to authorize guests. This solution was designed to be secure, require little maintenance and cost less to operate than similar service available. The final milestone will be to make setup user friendly as the current initialization has many steps and requires many steps.

## Technologies Chosen
Zappa: A Python library designed for hosting a RESTful Flask server on lambda functions. It quickly spins up the server on request and provides tools for easy deployment to the function. Chosen to reduce cost of hosting a webserver that would not get much traffic
AWS Lambda: Lightweight hosting option that runs only when queried. Chosen for its pay as used cost 
Python Flask: Mostly chosen to familiar with the language and variety of libraries that would help overcoming making these technologies work together
Twilio: Needed a phone number with programable API. Selected due to customizability and lack of other options.

## Issues
- Does not use Twilio's authorization token, spoke with a support to try and resolve the issue to no avail. will continue to implement it in the dev branch
- Error message over phone when unauthorized. view issues tab for details
- setup is long

## Setup Tutorial
If there is interest I will make a setup tutorial, if there is a lot of interest I simplify the setup process
