## -*- coding: iso-8859-1 -*-
from datetime import datetime, timedelta
import caldav
from os import remove
from icalendar import Calendar, Event

url = 'http://XXX.XXX.X.XXX:XXXX/'
userN = 'USERNAME'
passW = 'PASSWORD'

# CalDAV info
def load_cache(name):
    #### Loading calenderinformation for the local backup 
    termine = []
    try:
        event_file = open(name,"r")
    except:
        return None
    lines = event_file.readlines()
    for line in lines:
        if line.find("<cache>") != -1:
            collums = ["name","description","location","time","day"]
            iter = 0
        elif line.find("<end>") != -1:
            termine.append(collums)
        elif line.find(collums[iter])!= -1:
            temp = line[line.find(":")+1:line.find("\n")]
            if temp == 'None':
                temp = None
            elif iter == 3:
                temp = datetime.strptime(temp,'%H:%M:%S').time()
            elif iter == 4:
                temp = int(temp)
            collums[iter] = temp
            iter = iter + 1           
    return termine

class MyCalendar(object):
    def __init__(self,url,userN,passW):
        self.url = url
        self.userN = userN
        self.passW = passW
        self.cache = []
    
    def correct_encoding(self,string):
        #### Due to strang unicode stuff i have replace strange signs
        artis = ['\\xc3\\x9f','\\xc3\\x84','\\xc3\\x96','\\xc3\\x9c','\\xc3\\xa4','\\xc3\\xb6','\\xc3\\xbc','\\']
        realis = ['�','�','�','�','�','�','�',' ']
        for x , art in enumerate(artis):
            string = string.replace(art,realis[x])
        return string
        
    def syncronize(self):
        #stupid converion stuff
        client = caldav.DAVClient(url=self.url, username=self.userN, password=self.passW) #### Getting information from the caldav server
        principal = client.principal()
        calendars = principal.calendars()
        termine = []
        if len(calendars) > 0:
            calendar = calendars[0]
            print ("Using calendar", calendar)
            results = calendar.events()
            #### Arranging Calenderinformation
            for eventraw in results:
                event = Calendar.from_ical(eventraw._data)
                for component in event.walk():
                    if component.name == "VEVENT":
                        tempname = repr(component.get('summary'))
                        tempname = tempname[tempname.find('vText')+7:-2]
                        tempdesc = component.get('description')
                        tempstartDate = component.get('dtstart').dt
                        tempindex = tempstartDate.toordinal()
                        temploc =  component.get('location')
                        temprepeat = component.get('rrule')
                        if type(tempstartDate) == type(datetime.now()):
                            tempdate = tempstartDate.date()
                            temptime = tempstartDate.time()
                        else:
                            tempdate = tempstartDate
                            temptime = None
                        if type(temprepeat) != type(None):
                            temprepeat = repr(temprepeat)
                            temprepeat = temprepeat[temprepeat.find('[\'')+2:temprepeat.find('\']')]
                        if type(temploc) != type(None):
                            temploc = self.correct_encoding(repr(temploc))
                            temploc = temploc[temploc.find('vText')+7:-2]
                        if type(tempdesc) != type(None):
                            tempdesc = self.correct_encoding(repr(tempdesc))
                            tempdesc = tempdesc[tempdesc.find('vText')+7:-2]
                        if tempindex >= datetime.now().toordinal() or temprepeat != None:
                            termine.append([tempname,tempdesc,temploc,tempdate,temptime,temprepeat,tempindex])
        termine.sort(key=lambda x:x[6])
        print(str(len(termine)) + " events syncronized.")
        return termine

    def save_events(self,termine):
        #saving all events to a file
        if len(termine) < 1:
            return -1
        #remove("events.dat")
        event_file = open("events.dat","w+")
        collums = ["name","description","location","date","time","pattern","timecode"]
        for event in termine:
            event_file.write("<event>\n")
            for index, collum in enumerate(collums):
                event_file.write(collum + ":" + str(event[index]) +"\n")
            event_file.write("<end>\n")
        event_file.close()
        return 0

    def load_events(self):
        #load events from cache file
        termine = []
        event_file = open("events.dat","r")
        lines =  event_file.readlines()
        for line in lines: # A rather stupid way to read frpom a text file
            if line.find("<event>") != -1:
                collums = ["name","description","location","date","time","pattern","timecode"]
                iter = 0
            elif line.find("<end>") != -1:
                termine.append(collums)
            elif line.find(collums[iter])!= -1:
                temp = line[line.find(":")+1:line.find("\n")]
                if temp == 'None':
                    temp = None
                if iter == 3 and temp != None:
                    temp = datetime.strptime(temp,'%Y-%m-%d').date()
                elif iter == 4 and temp != None:
                    temp = datetime.strptime(temp,'%H:%M:%S').time()
                elif iter == 6: #6.th line after the initial sequence
                    temp = int(temp)
                collums[iter] = temp
                iter = iter + 1           
        return termine

    def organize(self,termine):
        #organising todays weeks events
        recent=[]
        now = datetime.now()+timedelta(days = 1)
        now7 = now + timedelta(days = 6)
        for event in termine:
            if event[5] == 'YEARLY':
                event[3] = datetime(year = now.year , month = event[3].month , day = event[3].day).date()                
            elif event[5] == 'MONTHLY':
                event[3] = datetime(year = now.year , month = now.month , day = event[3].day).date()               
            if now.toordinal() <= event[6] <= now7.toordinal() or event[5]=='WEEKLY':
                recent.append([event[0],event[1],event[2],event[4],event[3].weekday()]) 
        self.cache = recent               
        return recent

    def today(self):
        # Get todays events
        recent = []
        now = datetime.now()+timedelta(days = 1) 
        for event in self.cache:
            if event[4] == now.weekday():
                recent.append(event)
        if len(recent) == 0:
            recent = None
        return recent

    def save_cache(self,events,name):
        # Saving Organized Calendar entries to a file for speaking
        if events==None:
            event_file = open(name,"w+")
            event_file.close()
            return -1
        event_file = open(name,"w+")
        collums = ["name","description","location","time","day"]
        for event in events:
            event_file.write("<cache>\n")
            for index, collum in enumerate(collums):
                event_file.write(collum + ":" + str(event[index]) +"\n")
            event_file.write("<end>\n")
        event_file.close()
        return 0

    def run(self,void):
        #### test function 
        try:
            termine = self.syncronize()
            self.save_events(termine)
        except Exception as e:
            print(e)
            print("Use local Backup")
            try:
                termine = self.load_events()
            except:
                print("No Cache found. Please connect the Pi to the Internet!")
                return -1
        weekly = self.organize(termine)
        daily = self.today()
        self.save_cache(weekly,"weekly.dat")
        self.save_cache(daily,"daily.dat")
        print("Calendar is now up to date.")
#ical = MyCalendar(url=url, userN = userN, passW=passW)
#ical.run(None)
