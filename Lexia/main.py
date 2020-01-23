'''
Created on 08.09.2018

@author: Phil
'''
import pyaudio
import time
import os
from terminmanager import MyCalendar
from random import randint
from math import sqrt
from sys import exit
from audioop import avg, rms
from struct import unpack
from pocketsphinx.pocketsphinx import *
from decoder import DecoderCore
from network import ComObj, WebServer
from statemachine import NewTranslator
from collections import deque
from multiprocessing import Process
from threading import Thread
from voice import NewVoice

MODELDIR = "/home/pi/Lexia/model"
url = 'http://XXX.XXX.X.XXX:XXXX/' #URL to the Calendarsevrer
userN = 'Smart'
passW = 'XXXX'

class MainCore(object):
    ### Main Decoder Loop ############################
    ### This Object contains all needed functions ####
    def __init__(self,com = object() ):
        config = Decoder.default_config()
        config.set_string('-hmm', os.path.join(MODELDIR, 'de-de/de-de'))
        config.set_string('-keyphrase', 'lexia')
        config.set_string('-dict', os.path.join(MODELDIR, 'de-de/de.dic'))
        config.set_float('-kws_threshold',1e-7)
        #### Setting the Pocketsphinx Decode configuration ####
        self.decoder = Decoder(config)
        self.ticks = 16000/1024
        #### Audiobuffer list object ####
        self.pre_vol = deque(maxlen = int(10*self.ticks))
        self.com = com
        #### PyAudio Stream Object ####
        self.stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, 
                        channels=1, 
                        rate=16000, 
                        input=True, 
                        frames_per_buffer=1024)
        #### Audio output object ####
        self.voice = NewVoice()
        #### Statemachine Object ####
        self.Translator = NewTranslator(self.voice)
        #### Pocketsphinx Decoder ####
        self.core = DecoderCore()
        #### Calendar API Object ###
        self.calendar = MyCalendar(url=url,passW = passW, userN = userN)
    
    def wait_for_noise(self,max_time = 60,time_delay = 0,sensty = 1.7,state = 0):
        #### This function until the volume is greater then the average noise multiplied by sensty
        #### It leaves when the max time is reached or a network command has changed the current state
        print("Waiting for noise...")
        self.stream.start_stream()
        avr_noise = deque(maxlen =70)
        noise = deque(maxlen=15)
        noise.append(0)
        count = 0
        while(sum(noise)<5 or 3*self.ticks > count):
            volume = rms(self.stream.read(1024),4)
            avr_noise.append(volume)
            count = count + 1
            if volume > sum(avr_noise)/len(avr_noise)*sensty:
                noise.append(1)
            else:
                noise.append(0)
            if count > max_time*self.ticks:
                self.stream.stop_stream()
                return -1
            if self.com.id != state:
                self.stream.stop_stream()
                return 1
        self.stream.stop_stream()
        time.sleep(time_delay)
        return 0
        
    def hotword_detect(self):
        #### Most of the time this function is active  #######
        #### It waits for the specific hotword #######
        self.stream.start_stream()
        print("Waiting for Hotword...")
        self.decoder.start_utt()
        while(self.decoder.hyp() is None):
            buf = self.stream.read(1024) # Reading from audiostream
            self.pre_vol.append(rms(buf,2))
            if buf:
                self.decoder.process_raw(buf,False,False) # Processing audiodata
            else:
                break
            if self.com.id!= 1: # Exit Procedure if the systemstate changes
                self.decoder.end_utt()
                self.stream.stop_stream()
                return 1
        print('Hotword detected!')
        self.decoder.end_utt()
        self.stream.stop_stream()
        self.voice.ding() 
        return 0

    def record_cmd(self,min_cmd = 1.5 ,max_cmd = 10 ,sil_lim = 1.5 ,wd_ps=0.3,wd_ln=1.5,sensty = 1.4):
        #### This function records a given time and then translates the recorded audio into words
        #### The second core is used to translate the audio drectly after the a chuck has been recorded
        core = Process(target=self.core.run_decoder, args=(self.core.get_pipe_end(),))
        core.start() # Creating a Process
        count = 0
        silence = deque(maxlen=int(sil_lim*self.ticks)) 
        grnd_vol = sum(self.pre_vol)/len(self.pre_vol)
        vol_sm = 0
        self.stream.start_stream() # Starting audio Stream
        print("Recording Commands ...")
        while (count < min_cmd*self.ticks or sum(silence)>5):
            buf = self.stream.read(1024)
            volume = (rms(buf,2)+vol_sm)/2 # Calculating average audio intensity
            vol_sm = volume
            self.core.decode(buf) # Sending audiodata to second core
            if volume/grnd_vol > sensty: 
                silence.append(1)
            else:
                silence.append(0)
            count = count + 1
            if (count > max_cmd*self.ticks or self.com.id != 2): # Exits the loop if max command time is reached
                break
        print("Command recorded !")
        self.core.decode(0)
        self.stream.stop_stream()
        words = self.core.get_words() #Aquiring words from the second core
        print(words)
        return words
    
    def record_ans(self,max_len = 30):
        return 0
    
    def sync_calendar(self):
        calendar_core = Process(target=self.calendar.run, args=(None,))
        calendar_core.start()
        print("Calendar status " + str(calendar_core.is_alive()))

    def run(self):
        self.voice.speak(["system/system_on"])
        self.sync_calendar()
        self.com.id = 1 #Current state of the system
        while(True):
            if self.com.id == 1: # Waiting for Hotwords
                if self.hotword_detect() == 0:
                    self.com.id = 2
            elif self.com.id == 2: # Recording Commands
                words = self.record_cmd()
                if self.com.id == 2:
                    if len(words)>=4:
                        self.com.id = self.Translator.translate_cmd(words) # Sending words to the Statelibrary
                    else:
                        self.com.id = 1
            elif self.com.id == 10: # Wait for noise mode Welcome Sequence
                print("Going into wake on noise mode.")
                result = self.wait_for_noise(time_delay=8,sensty=1.6,state=10)
                if result == 0:
                    self.Translator.translate_cmd(self.com.str)
                    self.com.id = 1
                elif result == -1:
                    self.com.id = 1
            elif self.com.id == 11: # Wait for noise mode Morning Sequence
                print("Going into wake on noise mode.")
                self.sync_calendar()
                time.sleep(4*60)
                self.voice.speak(["casuals/morning"])
                self.voice.say_time()
                self.voice.say_weather_today()
                self.voice.say_events()
                for x in range(4): # Tries to wake up 4 times
                    result = self.wait_for_noise(sensty=1.8,state=11,max_time = 5*60)
                    if (result != -1):
                        break
                    self.voice.speak([["casuals/get_up","casuals/get_up_2","casuals/get_up_3","casuals/get_up_4"][x]])
                    time.sleep(1)
                    self.voice.say_time()
                if result == -1: 
                    self.Translator.lights_off()
                    self.com.id = 99 # Sleep state 99
                else:
                    self.com.id = 1 # Hotword state
            elif self.com.id == 42: # Translating Netwoek Command 
                self.com.id = self.Translator.translate_cmd(self.com.str)
            else:
                time.sleep(5)
        self.stream.close()

### Init modules
mycom = ComObj()
# Network Object
WebListener = WebServer(port= 0000,com = mycom)
NetProcessW = Thread(target=WebListener.run, args=())
NetProcessW.start() # Creating Thread

CoreMain = MainCore(com = mycom)
print("Webworking status " + str(NetProcessW.is_alive()))

CoreMain.run() 

