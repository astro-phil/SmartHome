# -*- coding: utf-8 -*-
'''
Created on 17.01.2018

@author: phil-
'''
from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM
import time
from voice import NewVoice
from math import copysign
from random import randint
from requests import get
from subprocess import call
from wakeonlan import send_magic_packet
from network import Pi2Pi
from threading import Thread


class NewTranslator():
    #### This object contains the connect between the spoken words and the commands to execute ####
    def __init__(self,voice = NewVoice()):
        print("Translator initialised!")
        self.string = ""
        self.voice = voice
        self.blue = Pi2Pi()

    def lights_off(self):
        try:
            self.blue.send("set_led9_mode=0_color=000000000")#led9 means all LEDS
        except:
            print("Could not reach lightnode.")
        return 0

    def answer_neg(self):
        rnd = randint(0,5)
        words=[["casuals/sorry"],["casuals/sorry"],["casuals/sorry_2"],["casuals/sorry_2"],["casuals/repeat"],["casuals/sorry_2","casuals/repeat"]]
        self.voice.speak(words[rnd])
        if rnd >= 4:
            return 2
        return 1
    
    def translate_ans(self,string = None):
        return 0

    def translate_cmd(self,string = None):
        if string != None:
            self.string = string

        ### Weclome Section ######################################
        key1 = self.string.find("hallo")
        if(key1 >= 0):
            text = [['casuals/welcome_home'],['casuals/welcome_back'],['casuals/hallo'],['casuals/hallo_2'],['casuals/i_bims']][randint(0,4)]
            if "kim" in self.string:
                text.append( ['people/kim','people/darling','people/best_kim','people/kim'][randint(0,3)])
            elif "philipp" in self.string:
                text.append(['people/philipp','people/imperator','people/mi_lord','people/philipp','people/philipp'][randint(0,4)])
            elif "max" in self.string:
                text.append(['people/max','people/imperator','people/max'][randint(0,2)])
            self.voice.speak(text)
            return 1

        key1 = self.string.find("heim")
        if(key1>=0):
            string = self.string.split(" ")
            text = ['people/'+string[2]]
            text.append(['casuals/comes_home','casuals/comes_door','casuals/comes_home_2'][randint(0,2)])
            self.voice.speak(text)
            return 1
        ### Light Section ########################################
        key1 = self.string.find("licht") 
        if(key1 >= 0):
            modes = [("automatik",1),("pulsieren",2)]
            leds = [("schrank",1),("tisch",2),("bett",0)]
            colors = [("an","030050100"),
                     ("aus","000000000"),
                     ("weiss","030050100"),
                     ("pink","330100100"),
                     ("rot","000100100"),
                     ("blau","200100100"),
                     ("gruen","120100100"),
                     ("gelb","040100100"),
                     ("orange","030100100"),
                     ("lila","240100100")]
            speak = ""
            led_id = 9
            for led in leds:
                if 0<self.string.find(led[0])<key1:
                    led_id = led[1]
                    break
            mode_id = 0
            for mode in modes:
                if self.string.find(mode[0])>key1:
                    mode_id = mode[1]
                    speak = "colors/"+mode[0]
                    break
            color_id = -1
            for color in colors:
                if self.string.find(color[0])>key1:
                    color_id = color[1]
                    speak = "colors/"+color[0]
                    break
            if color_id != -1 or mode_id > 0:
                if color_id == -1:
                    color_id = "000000000"
                ### Answering ###
                if randint(1,15) == 9 and mode_id == 0 and speak !="colors/an" and speak != "colors/aus":
                    color = colors[randint(2,len(colors)-1)]
                    color_id = color[1]
                    better = ["colors/better","colors/better_2"]
                    words = ["colors/"+color[0],better[randint(0,1)]]
                    voice = Thread(target = self.voice.speak,args=(words,))
                    voice.start()
                else:
                    words=[["casuals/okay"],["casuals/okay_2"],["colors/light_to",speak]]
                    if speak == "colors/an":
                        words[2]=["colors/lights_on"]
                    elif speak == "colors/aus":
                        words[2] =["colors/lights_off"]
                    voice = Thread(target= self.voice.speak,args=(words[randint(0,2)],))
                    voice.start()
                try:
                   self.blue.send("set_led"+str(led_id)+"_mode="+str(mode_id)+"_color="+color_id)
                except:
                    print("Could not reach lightnode.")
                    if randint(0,5) == 5:
                        self.voice.speak(["system/lightnode_no"])
                    else:
                        self.voice.speak(["casuals/sorry"])
                        self.voice.speak([["system/lightnode_off"],["system/lightnode_off_2"]][randint(0,1)])
                voice.join()
                return 1
            else:
                return self.answer_neg()
        ### Computer Section #########################################
        key1 = self.string.find("computer") + self.string.find("rechner") + 1
        if(key1 >= 0):
            key3 = self.string.find("aus")
            key2 = self.string.find("philipps") 
            if( len("philipps")+2 > key1-key2 > 0 and key2!=-1):
                if (key3 != -1):
                    print("Try to shutdown Philipp's computer")
                    words = [["casuals/okay"],["casuals/okay_2"]]
                    voice = Thread(target = self.voice.speak, args = (words[randint(0,1)],))
                    voice.start()
                    call(['net', 'rpc', '-S', 'XXX.XXX.X.XXX', '-U','USERNAME%PASSWORD', 'shutdown', '-t','1', '-f'])
                else:
                    print("Try to wake up Philipp's computer")
                    words = [["system/computer"],["casuals/okay"],["casuals/okay_2"]]
                    voice = Thread(target = self.voice.speak, args = (words[randint(0,2)],))
                    voice.start()
                    send_magic_packet('XX.XX.XX.XX.XX.XX') #WakeonLan
                voice.join()
                return 1
            key2 = self.string.find("kims") 
            if(len("kims")+2 > key1-key2 > 0 and key2!=-1):
                if (key3 != -1):
                    print("Try to shutdown Kim's computer")
                    words = [["casuals/okay"],["casuals/okay_2"]]
                    voice = Thread(target = self.voice.speak, args = (words[randint(0,1)],))
                    voice.start()
                    call(['net', 'rpc', '-S', 'XXX.XXX.X.XXX', '-U','USERNAME%PASSWORD', 'shutdown', '-t','1', '-f'])
                else:
                    print("Try to wake up Kim's computer")
                    words = [["system/computer"],["casuals/okay"],["casuals/okay_2"]]
                    voice = Thread(target = self.voice.speak, args = (words[randint(0,2)],))
                    voice.start()
                    send_magic_packet('XX.XX.XX.XX.XX.XX') #WakeonLan
                voice.join()
                return 1
            if randint(1,3) == 3:
                self.voice.speak(["system/computer_nein"])
                return 1
            return self.answer_neg()
        
        ### Time Section ##############################################
        if "uhr" in self.string:
            self.voice.say_time()
            return 1
        ### Joke section #############################################
        if "witz" in self.string:
            self.voice.joke()
            return 1
        ### Weather section ##########################################
        if "wetterbericht" in self.string:
            self.voice.say_weather_today()
            return 1
        if "wetter" in self.string:
            self.voice.say_weather()
            return 1
        ### Calendar Section ##########################################
        if "was steht an" in self.string:
            self.voice.say_events_today(True)
            return 1
        if "wochenbericht" in self.string:
            self.voice.say_events_week(True)
            return 1
        ### Netwrork Section #########################################
        if "nein" in self.string:
            return 1
        if "standby" in self.string:
            self.voice.speak(["system/speak_off"])
            return 99
        if "wach auf" in self.string:
            self.voice.speak(["system/speak_on"])
            return 1
        if "alles aus" in self.string:
            call(['net', 'rpc', '-S', 'XXX.XXX.X.XXX', '-U','USERNAME%PASSWORD', 'shutdown', '-t','1', '-f']) #remote Shutdown for Windows
            call(['net', 'rpc', '-S', 'XXX.XXX.X.XXX', '-U','USERNAME%PASSWORD', 'shutdown', '-t','1', '-f']) #remote Shutdown for Windows
            return 99
        if "gute nacht" in self.string:
            self.voice.speak([["casuals/night"],["casuals/night_2"],["casuals/night_3"],["casuals/night"],["casuals/night_2"]][randint(0,4)])
            return 99
        return 1