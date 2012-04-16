# Race Date Setter Application

What is this thing?
-------------------

The Race Date Setter application is a web application currently running on Google App Engine.  This application will take predefined running schedules, read them from the source website, store them in a database, schedule them on the user's Google calendar, and display the new training program in the application from Google calendar.

What makes this work?
---------------------

     o index.yaml
     o app.yaml
     o index.py (main program, handlers, and db models)
     o HalfMarathonProgram.py
     o MarathonProgram.py
     o Templates, which include
          o _base.htm
          o calendarcontent.htm
          o calendars.htm
          o index.htm
          o loaddb.htm
          o loginscreen.htm
          o programs.htm
     o Static files, which include
          o bar.gif
          o glike.css

You didn't do all of this did you?
----------------------------------

No, this project includes the following libraries:

Python:

     o apiclient
     o BeautifulSoup
     o httplib2
     o oauth2client
     o util.Sessions

JavaScript:

     o jquery-1.7.1
     o jquery.datepick

Cool! How do I run this thing?
-------------------------------

The latest build of the software is hosted on Google App Engine at http://racedatesetter.appspot.com.  You can download the source code yourself and run this project under the Google App Engine SDK.  Locally I have this running under SDK version 1.6.2.  This SDK version runs Python version 2.5.

Hmmm, what if something changes?
--------------------------------

You can see all changes below:

2012-02-29 David Simandl david.simandl@gmail.com

    o initial version

2012-03-07 David Simandl david.simandl@gmail.com

    o Added user check on the individual handlers.  If the user isn't
      logged in the redirect to the index page

2012-03-31 David Simandl david.simandl@gmail.com

    o Added user profile info page, updated index.py to handle this page

2012-03-31 David Simandl david.simandl@gmail.com

    o Changed the app.yaml and added cron.yaml files in order to support
      cron script for daily emails.

2012-04-16 David Simandl david.simandl@gmail.com

    o Changed the index.py file to allow for email notifications via a
      cron job and the app engine task que

2012-04-16 David Simandl david.simandl@gmail.com

    o Note, on this date I deleted the old repro on GitHub.  From this
      date on this changelog will be in sync with GitHub.  Changes previous       to this deletion are above...



Hey! Your software is buggy!
---------------------------

Contact me at david.simandl@gmail.com.  Or, feel free to fork this project at will and if you want to contribute issue a Pull Request.

Who are you?
-------------------------

This program was written by David Simandl.  I'm a software developer and avid runner living in Brooklyn, NY.  This is my first Python project although I have written code in other languages for years (Java).
