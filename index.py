import os
import logging
import wsgiref.handlers
import datetime
import httplib2
import pickle
from HalfMarathonProgram import HalfMarathonProgram
from MarathonProgram import MarathonProgram
from apiclient.discovery import build
from apiclient.errors import HttpError
from google.appengine.runtime import DeadlineExceededError
from oauth2client.appengine import CredentialsProperty
from oauth2client.appengine import StorageByKeyName
from oauth2client.client import OAuth2WebServerFlow
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.api import urlfetch
from util.sessions import Session
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail
from google.appengine.api import memcache
from google.appengine.api import taskqueue


# Look into mapReduce for the DB interactions

# A Model for a training program

class Program(db.Model):
    programName = db.StringProperty()
    programURL = db.StringProperty()

# A Model for the training program weeks

class programWeeks(db.Model):
    program = db.ReferenceProperty()
    week = db.IntegerProperty()
    monday = db.StringProperty()
    tuesday = db.StringProperty()
    wednesday = db.StringProperty()
    thursday = db.StringProperty()
    friday= db.StringProperty()
    saturday = db.StringProperty()
    sunday = db.StringProperty()

# A Model for user credentails for OAuth

class Credentials(db.Model):
    credentials = CredentialsProperty()

# A Model for created calendar HTML page (Google calendar can't
# get the HTML via the API at this time....

class calendarHTML(db.Model):
    userid = db.StringProperty()
    calendarId = db.StringProperty()
    calendarName = db.StringProperty()
    calendarTimeZone = db.StringProperty()
    calendarHTML = db.StringProperty()

# A Model for the user's profile and settings

class userProfile(db.Model):
    userid = db.StringProperty()
    firstname = db.StringProperty()
    lastname = db.StringProperty()
    emailaddress = db.StringProperty()
    notificationsetting = db.StringProperty()

# a page for our scrapper program

class Page():
    
    def get_page(self, url):
        page = urlfetch.fetch(url)
        logging.info(page.status_code)
        if page.status_code == 200:
            return page.content

# one whole program

class wholeProgram():

    def get_program(self, url):
        page = Page()
        page = page.get_page(url)
        if url == 'http://runningtimes.com/Article.aspx?ArticleID=5998':
            HalfProgram = HalfMarathonProgram(page)
            return HalfProgram.get_half_marathon_program()
        elif url == 'http://runningtimes.com/Article.aspx?ArticleID=5995':
            FullProgram = MarathonProgram(page)
            return FullProgram.get_marathon_program()


class dbQuery():

    def get_results(self, dbObject, fetchlimit=None, filtervals=[]):
        que = db.Query(dbObject)
        for filterval in filtervals:
            que = que.filter(filterval['operator'], filterval['value'])
        results = que.fetch(limit=fetchlimit)
        return results


def doRender(handler, tname='index.htm', values={}):
    temp = os.path.join(os.path.dirname(__file__),'templates/' + tname)
    if not os.path.isfile(temp):
        return False
    # Make a new copy of the dictonary and add the path
    newval = dict(values)
    newval['path'] = handler.request.path
    user = users.get_current_user()
    if user:
        if users.is_current_user_admin() == True:
            # wasn't able to use the bool true in the template for some
            # reason....
            newval['admin'] = 'True'
        newval['username'] = user.nickname()
        newval['logout'] = users.create_logout_url("/")
    outstr = template.render(temp, newval)
    handler.response.out.write(outstr)
    return True

class LoginHandler(webapp.RequestHandler):

    @login_required
    def get(self):
        self.session = Session()
        user = users.get_current_user()
        credentials = StorageByKeyName(Credentials, user.user_id(), 'credentials').get()
        self.session['creds'] = credentials

        if credentials:
            doRender(self, 'index.htm', { } )
        else:
            flow = OAuth2WebServerFlow(
                    response_type='code',
                    client_id='519209407557.apps.googleusercontent.com',
                    client_secret='wVwC3WD2Dl1GrrXpK3OgKaD3',
                    scope='https://www.googleapis.com/auth/calendar',
                    approval_prompt='force',
                    user_agent='racedatesetter/1.0')
            callback = self.request.relative_url('/auth_return')
            authorize_url = flow.step1_get_authorize_url(callback)
            memcache.set(user.user_id(), pickle.dumps(flow))
            self.redirect(authorize_url)

class OAuthHandler(webapp.RequestHandler):

    @login_required
    def get(self):
        user = users.get_current_user()
        flow = pickle.loads(memcache.get(user.user_id()))
        if flow:
            credentials = flow.step2_exchange(self.request.params)
            StorageByKeyName(Credentials, user.user_id(),
                    'credentials').put(credentials)
            self.redirect('index.htm')
        else:
            pass

class LogoutHandler(webapp.RequestHandler):

    def get(self):
        self.session = Session()
        self.session.delete_item('username')
        self.session.delete_item('userkey')
        doRender(self, 'index.htm')

class LoadDBHandler(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user is None:
            self.redirect('index.htm')
        else:
            doRender(self, 'loaddb.htm')

    def post(self):
        programname = self.request.get('program')
        program = wholeProgram()
        trainingProgram = program.get_program(programname)

        if len(trainingProgram) > 0:
            que = db.Query(Program)
            que = que.filter('programURL = ',programname)
            results = que.fetch(limit=1)
            if len(results) > 0:
                doRender(self, 'loaddb.htm', {'error' : 'The training program already exists!'})
            else:
                if programname == 'http://runningtimes.com/Article.aspx?ArticleID=5998':
                    newProgram = Program(programName='Running Times - Half Marathon Basic', programURL=programname)
                    pkey = newProgram.put()
                elif programname == 'http://runningtimes.com/Article.aspx?ArticleID=5995':
                    newProgram = Program(programName='Running Times - Marathon Advanced', programURL=programname)
                    pkey = newProgram.put()
                for week, daysDistance in enumerate(reversed(trainingProgram)):
                    newWeek = programWeeks(program=pkey, week=week, monday=unicode(daysDistance['Monday']),
                            tuesday=unicode(daysDistance['Tuesday']),
                            wednesday=unicode(daysDistance['Wednesday']),
                            thursday=unicode(daysDistance['Thursday']),
                            friday=unicode(daysDistance['Friday']),
                            saturday=unicode(daysDistance['Saturday']),
                            sunday=unicode(daysDistance['Sunday']))
                    newWeek.put()
                doRender(self, 'index.htm', { })
        else:
            doRender(self, 'loaddb.htm', {'error' : 'The program is empty!'})

class ProgramHandler(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user is None:
            self.redirect('index.htm')
        else:
            que = db.Query(Program)
            program_list = que.fetch(limit=100)
            doRender(self, 'programs.htm', {'program_list' : program_list})

    def post(self):
        user = users.get_current_user()
        creds = StorageByKeyName(Credentials, user.user_id(), 'credentials').get()
        http = httplib2.Http()
        http = creds.authorize(http)
        service = build(serviceName='calendar', version='v3', http=http,
                developerKey='AIzaSyD51wdv-kO02p29Aog7OXmL2eEG0F5ngZM')
        programname = self.request.get('program')
        racedate = self.request.get('racedate')
        calsummery = self.request.get('calsummery')
        callocation = self.request.get('location')
        racedate = datetime.datetime.strptime(racedate, '%m/%d/%Y')
        racedate = racedate.date()
        programQuery = db.Query(Program)
        programQuery = programQuery.filter('programName = ', programname)
        results = programQuery.fetch(limit=1)

        # Had some difficuty building doing a POST to the REST API, will just
        # use the provided python API instead
        # url = 'https://www.googleapis.com/calendar/v3/calendars?pp=1&key=AIzaSyD51wdv-kO02p29Aog7OXmL2eEG0F5ngZM'
        
        newcal = {
                'summary': calsummery,
                'timezone': callocation
        }
        try:
            created_calendar = service.calendars().insert(body=newcal).execute()
            storedcalendar = calendarHTML(userid=user.user_id(), 
                    calendarId = created_calendar['id'],
                    calendarName = created_calendar['summary'],
                    calendarTimeZone = callocation,
                    calendarHTML='<iframe src="https://www.google.com/calendar/embed?src='+created_calendar['id']+'&ctz='+callocation+'" style="border:0" width="800" height="600" frameborder="0" scrolling="no"></iframe>')
            storedcalendar.put()
        except(DeadlineExceededError, HttpError):
            doRender(self, 'index.htm', {'error' : 'There was an error on submit, please try again'})
        #resp, content = http.request(url, method='POST', body=newcal)
        
        if len(results) > 0:
            programReturned = results[0]
            programWeeksQuery = db.Query(programWeeks)
            programWeeksQuery.filter('program = ',
                    programReturned.key())
            programWeeksQuery.order('week')
            results = programWeeksQuery.fetch(limit=100)

            # would like to figure out how to use a jquery progress bar
            # here, will user an generic spinner annimation instead

            if len(results) > 0:
                for result in reversed(results):
                    event = {
                            'summary': result.sunday,
                            'location': callocation,
                            'start': {
                                'date': str(racedate)
                            },
                            'end' : {
                                'date': str(racedate)
                                }
                            }
                    try:
                        created_event = service.events().insert(calendarId=created_calendar['id'],
                            body=event).execute()
                    except(DeadlineExceededError, HttpError):
                        doRender(self, 'index.htm', {'error' : 'There was an error on submit, please try again'})
                        break
                    racedate = racedate + datetime.timedelta(days=-1)
                    event = {
                            'summary': result.saturday,
                            'location': callocation,
                            'start': {
                                'date': str(racedate)
                            },
                            'end' : {
                                'date': str(racedate)
                                }
                            }
                    try:
                        created_event = service.events().insert(calendarId=created_calendar['id'],
                            body=event).execute()
                    except(DeadlineExceededError, HttpError):
                        doRender(self, 'index.htm', {'error' : 'There was an error on submit, please try again'})
                        break
                    racedate = racedate + datetime.timedelta(days=-1)
                    event = {
                            'summary': result.friday,
                            'location': callocation,
                            'start': {
                                'date': str(racedate)
                            },
                            'end' : {
                                'date': str(racedate)
                                }
                            }
                    try:
                        created_event = service.events().insert(calendarId=created_calendar['id'],
                            body=event).execute()
                    except(DeadlineExceededError, HttpError):
                        doRender(self, 'index.htm', {'error' : 'There was an error on submit, please try again'})
                        break
                    racedate = racedate + datetime.timedelta(days=-1)
                    event = {
                            'summary': result.thursday,
                            'location': callocation,
                            'start': {
                                'date': str(racedate)
                            },
                            'end' : {
                                'date': str(racedate)
                                }
                            }
                    try:
                        created_event = service.events().insert(calendarId=created_calendar['id'],
                            body=event).execute()
                    except(DeadlineExceededError, HttpError):
                        doRender(self, 'index.htm', {'error' : 'There was an error on submit, please try again'})
                        break
                    racedate = racedate + datetime.timedelta(days=-1)
                    event = {
                            'summary': result.wednesday,
                            'location': callocation,
                            'start': {
                                'date': str(racedate)
                            },
                            'end' : {
                                'date': str(racedate)
                                }
                            }
                    try:
                        created_event = service.events().insert(calendarId=created_calendar['id'],
                            body=event).execute()
                    except(DeadlineExceededError, HttpError):
                        doRender(self, 'index.htm', {'error' : 'There was an error on submit, please try again'})
                        break
                    racedate = racedate + datetime.timedelta(days=-1)
                    event = {
                            'summary': result.tuesday,
                            'location': callocation,
                            'start': {
                                'date': str(racedate)
                            },
                            'end' : {
                                'date': str(racedate)
                                }
                            }
                    try:
                        created_event = service.events().insert(calendarId=created_calendar['id'],
                            body=event).execute()
                    except(DeadlineExceededError, HttpError):
                        doRender(self, 'index.htm', {'error' : 'There was an error on submit, please try again'})
                        break
                    racedate = racedate + datetime.timedelta(days=-1)
                    event = {
                            'summary': result.monday,
                            'location': callocation,
                            'start': {
                                'date': str(racedate)
                            },
                            'end' : {
                                'date': str(racedate)
                                }
                            }
                    try:
                        created_event = service.events().insert(calendarId=created_calendar['id'],
                            body=event).execute()
                    except(DeadlineExceededError, HttpError):
                        doRender(self, 'index.htm', {'error' : 'There was an error on submit, please try again'})
                        break
                    racedate = racedate + datetime.timedelta(days=-1)
                doRender(self, 'index.htm', {'programloaded' : 'The program was loaded to your calendar successfully'})
            else:
                doRender(self, 'index.htm', {'error' : 'No weeks were returned from the database!'})
        else:
            doRender(self, 'index.htm', {'error' : 'No programs returned from the DB!'})


class ListCalendars(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user is None:
            self.redirect('index.htm')
        else:
            filterdiclist = [{'operator' : 'userid = ', 'value':
                user.user_id()}, {'operator' : 'calendarHTML != ', 'value': None}]
            query = dbQuery()
            calendar_list = query.get_results(calendarHTML, 100, filterdiclist)
            doRender(self, 'calendars.htm', {'calendar_list' : calendar_list})

    def post(self):
        self.session = Session()
        self.session['selectedcal'] = self.request.get('calendarname')
        # this reuses the get code at the end of the post
        self.get()

class CalendarHandler(webapp.RequestHandler):

    def get(self):
        self.session = Session()
        filterdiclist = [{'operator' : 'calendarName = ', 'value' :
            self.session['selectedcal']}]
        query = dbQuery()
        calendar_list = query.get_results(calendarHTML, 1, filterdiclist)
        doRender(self, 'calendarcontent.htm', {'calendarcontent' :
            calendar_list[0]})


class UserProfileHandler(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user is None:
            self.redirect('index.htm')
        else:
            filterdiclist = [{'operator' : 'userid = ', 'value' : user.user_id()}]
            query = dbQuery()
            user_list = query.get_results(userProfile, 1, filterdiclist)
            if not user_list:
                doRender(self, 'userprofile.htm', { })
            else:
                memcache.set(key=user.user_id(), value=user_list[0])
                doRender(self, 'userprofile.htm', {'user_list' : user_list[0]})

    def post(self):
        user = users.get_current_user()
        if user is None:
            self.redirect('index.htm')
        else:
            profilerecord = memcache.get(key=user.user_id())
            firstname = self.request.get('firstname')
            lastname = self.request.get('lastname')
            emailaddress = self.request.get('emailaddress')
            emailnotification = self.request.get('notifications')
            if profilerecord is not None:
                profilerecord.firstname = firstname
                profilerecord.lastname = lastname
                profilerecord.emailaddress = emailaddress
                profilerecord.notificationsetting = emailnotification
                memcache.delete(key=user.user_id())
                profilerecord.put()
            else:
                profile = userProfile(userid=user.user_id(), firstname=firstname,
                        lastname=lastname, emailaddress=emailaddress,
                        notificationsetting=emailnotification)
                profile.put()
            doRender(self, 'index.htm', { })


class CronHandler(webapp.RequestHandler):

    def get(self):
        # I have assumed that this is a US only based web site.  If this
        # changes I will grow the list and modify the code in the future.
        # This list maps backwards from Eastern Time / New York.  (IE, NY
        # Eastern is 00, Chicago Central is -01, etc.  This does not adjust for
        # "Summer Time", ie daylight savings time
        bigtimezonedic = {'America/New_York' : 0, 'America/Detroit' : 0, 'America/Kentucky/Louisville' : 0, 'America/Kentucky/Monticello' : 0, 'America/Indiana/Indianapolis' : 0, 'America/Indiana/Vincennes' : 0, 'America/Indiana/Winamac' : 0, 'America/Indiana/Marengo' : 0, 'America/Indiana/Petersburg' : 0, 'America/Indiana/Vevay' : 0, 'America/Chicago' : 1, 'America/Indiana/Tell_City' : 1, 'America/Indiana/Knox': 1, 'America/Menominee' : 1, 'America/North_Dakota/Center' : 1, 'America/North_Dakota/New_Salem' : 1, 'America/Denver' : 2, 'America/Boise' : 2, 'America/Shiprock' : 2, 'America/Phoenix' : 2, 'America/Los_Angeles' : 3, 'America/Anchorage' : 4, 'America/Juneau' : 4, 'America/Yakutat' : 4, 'America/Nome' : 4, 'America/Adak' : 5, 'Pacific/Honolulu' : 5}
        # We are just grabbing the TimeZone from the calendarHTML table, which
        # might turn into an actual calendar table when we make our own cal and
        # just sync with google cal instead of letting google cal completely
        # host it
        calendar_list = calendarHTML.all()
        for calendar in calendar_list:
             if bigtimezonedic.has_key(calendar.calendarTimeZone):
                 if bigtimezonedic[calendar.calendarTimeZone] == 0:
                    taskqueue.add(url='/emailsender',
                            params=dict(calendaruserid=calendar.userid,
                                calendarid=calendar.calendarId))
                 else:
                    taskqueue.add(url='/emailsender',
                            params=dict(calendaruserid=calendar.userid,
                                calendarid=calendar.calendarId),
                         eta=datetime.datetime.now() +
                         datetime.timedelta(hours=bigtimezonedic[calendar.calendarTimeZone]))
             else:
                logging.info('There is an unsupported timezone!')
                

class EmailSenderHandler(webapp.RequestHandler):

    def post(self):
        calendaruserid = self.request.get('calendaruserid')
        calendarid = self.request.get('calendarid')
        creds = StorageByKeyName(Credentials, calendaruserid, 'credentials').get()
        http = httplib2.Http()
        http = creds.authorize(http)
        service = build(serviceName='calendar', version='v3', http=http,
                developerKey='AIzaSyD51wdv-kO02p29Aog7OXmL2eEG0F5ngZM')
        events = service.events().list(calendarId=calendarid).execute()
        for event in events['items']:
            if str(datetime.date.today()) == event['start']['date']:
                filterdiclist = [{'operator' : 'userid = ', 'value' :
                            calendaruserid},{'operator' : 'notificationsetting = ', 'value' : 'Yes'}]
                query = dbQuery()
                user_list = query.get_results(userProfile, 1,
                                filterdiclist)
                mail.send_mail(sender="support@racedatesetter.appspotmail.com",
                                       to=user_list[0].emailaddress,
                                       subject="Here is your run today!",
                                       body="""
Dear """ + user_list[0].firstname + """ """ + user_list[0].lastname + """

Your run today is the following: 
""" +

event['summary'] + """

Thanks!

The race date setter app!""" )

class MainHandler(webapp.RequestHandler):
    
    def get(self):
        if doRender(self, self.request.path):
            return
        doRender(self, 'index.htm')

def main():
    application = webapp.WSGIApplication([
        ('/index', LoginHandler),
        ('/auth_return', OAuthHandler),
        ('/logout', LogoutHandler),
        ('/loaddb', LoadDBHandler),
        ('/programs', ProgramHandler),
        ('/calendars', ListCalendars),
        ('/calcontent', CalendarHandler),
        ('/userprofile', UserProfileHandler),
        ('/jobs', CronHandler),
        ('/emailsender', EmailSenderHandler),
        ('/.*', MainHandler)],
            debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()

