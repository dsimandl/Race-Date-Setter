try:
    from xml.etree import ElementTree
except ImportError:
    from elementtree import ElementTree
import gdata.calendar.data
import gdata.calendar.client
import gdata.acl.data
import atom.data
import time

client = gdata.calendar.client.CalendarClient(source='David Test 01')
client.ClientLogin('david.simandl@gmail.com', '7912979t?', client.source)

calendar = gdata.calendar.data.CalendarEntry()
calendar.title = atom.data.Title(text='testcal4')
calendar.summary = atom.data.Summary(text='testcal1 discript')
calendar.where.append(gdata.calendar.data.CalendarWhere(value='New York City'))
calendar.color = gdata.calendar.data.ColorProperty(value='#2952A3')
calendar.timezone = gdata.calendar.data.TimeZoneProperty(value='America/New_York')

new_calendar = client.InsertCalendar(new_calendar=calendar)

feed = client.GetOwnCalendarsFeed()
for i, a_calendar in enumerate(feed.entry):
    if a_calendar.title.text == 'testcal3':
        event = gdata.calendar.data.CalendarEventEntry()
        event.content = atom.data.Content(text='test for 2011-11-15')
        event.quick_add = gdata.calendar.data.QuickAddProperty(value='true')
        new_event = client.InsertEvent(event, a_calendar.content.src)



