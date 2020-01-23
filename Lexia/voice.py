import pyaudio
import wave
import subprocess
from datetime import datetime
from random import randint
from weather import Weather
from terminmanager import load_cache
from os import remove
from time import sleep

class NewVoice(object):
    def __init__(self):
        temp = wave.open("/home/pi/Lexia/voice/ding.wav","rb")
        self.jokes = []
        self.frog = Weather()
        self.stream = pyaudio.PyAudio().open(format=pyaudio.PyAudio().get_format_from_width(temp.getsampwidth()), 
                        channels=2, 
                        rate=temp.getframerate(), 
                        output=True)
        #### Setting the Audiosetting by a test audiofile
        temp.close()

    def get_numbers(self,number):
        #### Converting numbers to text
        rest = number % 5
        number = number - rest
        state = "none"
        if rest > 2:
            state = "under"
            temp = temp + 5
        elif rest > 0:
            state = "over"
        return (state,number)

    def start_stream(self):
        self.stream.start_stream()
        return 0

    def stop_stream(self):
        self.stream.stop_stream()
        return 0

    def stream_wave(self,wave_file):
        CHUNK = 8*512
        SILENCE = ' '
        wav = wave.open(wave_file,"rb")
        buf = wav.readframes(CHUNK)
        while buf:
            buf = wav.readframes(CHUNK)
            self.stream.write(buf)
        free = self.stream.get_write_available() # How much space is left in the buffer?
        if free > CHUNK: # Is there a lot of space in the buffer?
            tofill = free - CHUNK
            self.stream.write(SILENCE * tofill) # Fill it with silence
        return 0
        
    def play(self,wave_file):
        #### Plays a wave file
        open(wave_file)
        subprocess.call(["aplay",wave_file])
        return 0
        
    def tts(self,lang,word):
        #### Fallback tts engine 
        word = word.split("/")
        if len(word)>1:
            word = word[1]
        else:
            word = word[0]
        subprocess.call(["pico2wave","--lang="+str(lang), "-w","temp.wav",word.replace("_"," ")])
        subprocess.call(["aplay","temp.wav"])
        remove("temp.wav")
        return 0

    def speak(self,words):
        #### Speak words
        for word in words:
            try:
                self.play("/home/pi/Lexia/voice/"+str(word)+".wav")
            except:
                print("Could not find "+ str(word)+".wav !")
                print("Fallback to TTS Engine")
                self.tts('en-US',word[word.find("/"):-1])
        return 0

    def get_time(self,minutes = 0, hours = 0):
        #### Converting current time into words
        if minutes+hours == 0:
            now = datetime.now()
            minutes = now.minute
            hours = now.hour
        rest = minutes % 5
        words = []
        if rest > 2:
            if minutes > 55:
                hours = hours + 1
            words.append("befor")
            minutes = minutes + 5
        elif rest > 0:
            words.append("after")
        if hours > 23:
            hours = 0
        words.append(str(hours))
        words.append("clock")
        if 57 > minutes > 3:
            words.append(str(minutes-rest))
        return words

    def say_time(self,minutes = 0, hours = 0):
        #### Converting time to audio
        if minutes+hours == 0:
            now = datetime.now()
            minutes = now.minute
            hours = now.hour
        rest = minutes % 5
        words = ["it_is"]
        if rest > 2:
            if minutes > 55:
                hours = hours + 1
            words.append("befor")
            minutes = minutes + 5
        elif rest > 0:
            words.append("after")
        if hours > 23:
            hours = 0
        words.append(str(hours))
        words.append("clock")
        if 57 > minutes > 3:
            words.append(str(minutes-rest))
        self.start_stream()
        #### Reading words ####
        for word in words:
            try:
                self.stream_wave("/home/pi/Lexia/voice/clock/"+str(word)+".wav")
            except:
                self.stop_stream()
                print("Could not find "+ str(word)+".wav !")
                print("Fallback to TTS Engine")
                self.tts('en-US',word)
                self.start_stream()
        self.stop_stream()
        return 0
        

    def joke(self):
        #### Reading jokes ####
        if len(self.jokes)<1:
            self.jokes = []
            for x in range(17):
                self.jokes.append("joke_"+str(x+1)+".wav")
        rnd = randint(1,len(self.jokes))-1
        try:
            self.play("/home/pi/Lexia/voice/jokes/"+self.jokes[rnd])
        except:
            print("Cloud not find /jokes/"+ self.jokes[rnd])
        self.jokes.remove(self.jokes[rnd])
        return 0

    def ding(self):
        self.play("/home/pi/Lexia/voice/ding.wav")
        return 0
    
    def say_weather(self):
        #### Reading the weather text
        state , temp , wind = self.frog.get_weather_now()
        weather_text = ["weather_now"]
        weather_text.append(state)
        weather_text.append("rec_temp_2")
        text = self.frog.get_temp(temp)
        for item in text:
            weather_text.append(item)
        weather_text.append('degree')
        weather_text.append("wind")
        text = self.frog.get_wind_num(wind)
        for item in text:
            weather_text.append(item)
        weather_text.append("kmh")
        self.start_stream()
        for word in weather_text:
            try:
                self.stream_wave("/home/pi/Lexia/voice/weather/"+str(word)+".wav")
            except:
                self.stop_stream()
                print("Could not find "+ str(word)+".wav !")
                print("Fallback to TTS Engine")
                self.tts('en-US',word)
                self.start_stream()
        self.stop_stream()
        return 0

    def say_weather_today(self):
        #### Reading the weatherforecast
        forecast , temp , wind = self.frog.get_weather_today()
        weather_text = ["weather_update"]
        thens = ["followed_by","next","then","then_2","after","after_2"]
        for index, item in enumerate(forecast):
            if index % 2 != 0:
                weather_text.append("until")
                weather_text.append(str(item))
                weather_text.append("clock")
                weather_text.append(thens[randint(0,5)])
            else:
                weather_text.append(item)
        weather_text.append("high_temp")
        text = self.frog.get_temp(temp[0][0])
        for item in text:
            weather_text.append(item)
        weather_text.append('degree')
        weather_text.append(["at","at_2","at_3"][randint(0,2)]) # Adding some variation
        weather_text.append(str(temp[0][1]))
        weather_text.append("clock")
        weather_text.append("low_temp")
        text = self.frog.get_temp(temp[1][0])
        for item in text:
            weather_text.append(item)
        weather_text.append('degree')
        weather_text.append(["at","at_2","at_3"][randint(0,2)]) # Adding some variation
        weather_text.append(str(temp[1][1]))
        weather_text.append("clock")
        weather_text.append("high_wind")
        text = self.frog.get_wind_num(wind[0])
        for item in text:
            weather_text.append(item)
        weather_text.append("kmh")
        weather_text.append(["at","at_2","at_3"][randint(0,2)]) # Adding some variation
        weather_text.append(str(wind[1]))
        weather_text.append("clock")
        self.start_stream()
        for word in weather_text:
            try:
                self.stream_wave("/home/pi/Lexia/voice/weather/"+str(word)+".wav")
            except:
                self.stop_stream()
                print("Could not find "+ str(word)+".wav !")
                print("Fallback to TTS Engine")
                self.tts('en-US',word)
                self.start_stream()
        self.stop_stream()
        return 0

    def say_events_week(self,use_text):
        #### Reading calenderinormation for the current week
        now = datetime.now()
        text = []
        birthday = []
        termine = []
        events = load_cache("weekly.dat")
        if events == None:
            print("No events for this week.")
            return -1
        for event in events:
            if event[0].find("Geburtstag") != -1:
                birthday.append(event)
            else:
                termine.append(event)
        if birthday != []:
            if len(birthday) > 1:
                if now.weekday() == 0:
                    text.append("this_week_have")
                else:
                    text.append("in_7_have")
            else:
                if now.weekday() == 0:
                    text.append("this_week_has")
                else:
                    text.append("in_7_has")
            for index,days in enumerate(birthday):
                text.append("names/"+days[0][0:days[0].find("hat")-1].replace(" ","_"))
                if index < len(birthday)-1:
                    text.append("and")
            text.append("birthday")
        if termine != []:
            if len(termine) >= 2:
                if now.weekday() == 0:
                    text.append("events")
                else:
                    text.append("events_7")
                last = 0
                for termin in termine:
                    if termin[4] != datetime.now().weekday():
                        if last != termin[4]:
                           	days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
                            text.append(days[termin[4]])
                        else:
                            text.append("and")
                        text.append(termin[0])
                    last = termin[4]
            else:
                termin = termine[0]
                if termin[4] != datetime.now().weekday():
                    if now.weekday() == 0:
                        text.append("event")
                    else:
                        text.append("event_7")
                   	days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
                    text.append(days[termin[4]])
                    text.append(termin[0])
        if len(text) < 1:
            if use_text:
                if now.weekday() == 0:
                    text.append("no_events")
                else:
                    text.append("no_events_7")
            else: 
                return -1
        self.start_stream()
        for word in text:
            try:
                self.stream_wave("/home/pi/Lexia/voice/events/"+str(word)+".wav")
            except:
                self.stop_stream()
                print("Could not find "+ str(word)+".wav !")
                print("Fallback to TTS Engine")
                self.tts('de-DE',word.replace('y','i'))
                self.start_stream()
        self.stop_stream()
        return 0

    def say_events_today(self,use_text = False):
        now = datetime.now().time()
        text = []
        birthday = []
        termine = []
        events = load_cache("daily.dat")
        if events == None:
            print("Nothing todo for today.")
            return -1
        else:
            for event in events:
                if event[0].find("Geburtstag") != -1:
                    birthday.append(event)
                else:
                    if event[3] > now: 
                        termine.append(event)
            if birthday != []:
                if len(birthday) > 1:
                    text.append("today_have")
                else:
                    text.append("today_has")
                for index,days in enumerate(birthday):
                    text.append("names/"+days[0][0:days[0].find("hat")-1].replace(" ","_"))
                    if index < len(birthday)-1:
                        text.append("and")
                text.append("birthday")
        if termine != []:
            if len(termine) > 1:
                text.append("events_today")
                for termin in termine:
                    text.append(termin[0])
                    if termin[1] != None:
                        text.append(termin[1])
                    if termin[2] != None:
                        text.append(termin[2])
                    if termin[3] != None:
                        text.append("at")
                        event_time = termin[3]
                        for word in self.get_time(hours=event_time.hour, minutes = event_time.minute):
                            text.append("clock/"+word)
            elif len(termine) == 1:
                termin = termine[0]
                text.append("event_today")
                text.append(termin[0])
                if termin[1] != None:
                    text.append(termin[1])
                if termin[2] != None:
                    text.append(termin[2])
                if termin[3] != None:
                    text.append("at")
                    event_time = termin[3]
                    for word in self.get_time(hours = event_time.hour, minutes = event_time.minute):
                        text.append("clock/"+word)  
        if len(text) < 1:
            if use_text:
                text.append("no_events_today")  
            else: 
                return -1 
        self.start_stream()
        for word in text:
            try:
                if word.find("clock") != -1:
                    self.stream_wave("/home/pi/Lexia/voice/"+str(word)+".wav")
                else:
                    self.stream_wave("/home/pi/Lexia/voice/events/"+str(word)+".wav")
            except:
                self.stop_stream()
                print("Could not find "+ str(word)+".wav !")
                print("Fallback to TTS Engine")
                self.tts('de-DE',word.replace('y','i'))
                self.start_stream()
        self.stop_stream()
        return 0

    def say_events(self):
        today = datetime.now().weekday()
        if today == 0:
            self.say_events_week(False)
            self.say_events_today(True)
        else:
            self.say_events_today(False)

