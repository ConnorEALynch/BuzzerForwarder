# BuzzerForwarder
## Introduction
Many apartments have deprecated lobby door authorization designed to route to a single home phone. in modern times the home phone is extinct replaced with the personal mobile phone. This software operates as a “man-in the-middle” to simultaneous ring the tenant’s phones, connect the first to pickup, allow them to converse and enter the code to authorize guests. This solution was designed to be secure, require little maintenance and cost less to operate than similar service available. The final milestone will be to make setup user friendly as the current initialization has many steps and requires many accounts and services.

## Version 2
After many months of seamless door answering, some bugs and a new inconvience emerged. With some slight reworking and the new mute feature added into version 2 of the Buzzer Forwarder, both problems have been gracefully answered. When either tenant is away from home or simply doesnt want to be disturbed, a quick text with a date or time now mutes the buzzer for that user. It accepts many date and time formats and the mute can be cut short by quickly typing unmute. Setting a timer was chosen over a simple toggle mute or unmute to avoid the inevitable problem of muting and forgetting. This approach has the benfit of setting and forgetting with the ease of toggling back on in an instant.

### Formats excepted
unmute - removes the current mute
8:33 AM - will be mute until the next occurence of that time
9/7 - will be mute until that date of the current time
Saturday - will be mute until that weekday of the current time
8:00 AM 9/7 - will be mute until that time and date. cannot specify year

## Setup Tutorial
Use production branch. dev is being tested
