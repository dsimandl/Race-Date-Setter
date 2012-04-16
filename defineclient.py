import gdata.calendar.data
import gdata.calendar.client
import gdata.acl.data

class DefineClient:
    def __init__(self, a_source, a_email, a_pw):
        self.source = a_source
        self.email = a_email
        self.pw = a_pw

    def SetClient(self):
        client = gdata.calendar.client.CalendarClient(source=self.source)
        client.ClientLogin(self.email, self.pw, self.source)
        return(client)

