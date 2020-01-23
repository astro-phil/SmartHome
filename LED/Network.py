import subprocess
import sys
import datetime
import socket
import threading
import bluetooth
from LED import NewLED
from PyQt5.QtCore import QThread, pyqtSignal
from time import sleep
from math import sin, cos, acos
from requests import get

class Pi2Pi(object):
    #### This Objects is used to Send information via HTTPRequest between 2 Raspberries
    def __init__(self, address = 'XXX.XXX.X.XXX',port = 0000):
        self.address = address
        self.port = port

    def send(self,msg):
        try:
            get('http://'+self.address+':'+str(self.port)+'/'+msg)
        except Exception as e:
            print(e)


class RemotePC(object):
    ##### Tjis is just for storig information
    def __init__(self):
        self.state = False
    def gets(self):
        return self.state
    def sets(self,val):
        self.state = val

class Phone(object):
    #### This Objetcs connects to a phone via Bluetooth and checks if it is in Range
    def __init__(self,mac,port,name):
        self.mac = mac #BL Mac adress of a phone
        self.state = False
        self.time = 0
        self.name = name # Name of the phones owner
        self.connect = None
        self.rssi = None
        self.port = port #BL Port

    def count(self): # Return the current state of the connection if timeedout or not
        self.time = self.time - 1
        if self.time < 0:
            return True
        else:
            return False

    def ping(self): # Pings the phone via BL
        if self.count():
            if not self.state:
                try: # Tries to establish the connection
                    self.connect = bluetooth.BluetoothSocket()
                    self.connect.connect((str(self.mac),self.port))
                    self.state = True
                    self.time = 30 #Max tryouts until the state is set to false
                    return True
                except Exception as e:
                    print("ERROR in Devicedetection")
                    print(e)
                    self.state = False
                    self.connect.close()
                    self.time = 2
                    return False
            else:
                self.rssi = subprocess.Popen(['hcitool','rssi',str(self.mac)],stdout=subprocess.PIPE,stderr = subprocess.STDOUT) #ping command
                output = self.rssi.stdout.readlines()
                print(output)
                self.time = 30
                if str(output[0]).find("Not connected")!=-1: 
                    self.state = False
                    self.time = 2
                return True
        else:
            return self.state

    def get_name(self):
        return self.name

    def get_time(self):
        return self.time

class AtHome(QThread):
    signal = pyqtSignal(bool,name = 'state')
    def __init__(self,lng,lat,tz,led = NewLED((0,0,0),0),blue = Pi2Pi(),rpc = RemotePC()):
        QThread.__init__(self)
        self.lng = lng #lat and long koordinates for sunrise and sunset calculation
        self.lat = lat
        self.tz = tz
        self.led = led
        self.blue = blue
        self.rpc = rpc

    def sunstate(self): # Returns if the sun has rised or set
        date = datetime.datetime.now()
        tag = int((date.month-1)*30.416+date.day+1)
        zeitgleichung =  -0.171*sin(0.0337 * tag + 0.465) - 0.1299*sin(0.01787 * tag - 0.168)
        deklination = 0.4095*sin(0.016906*(tag-80.086))
        breite = (self.lat/180)*3.14159
        zeitdifferenz = 12*acos((sin(-0.0145) - sin(breite)*sin(deklination)) / (cos(breite)*cos(deklination)))/3.14159
        aufgang   = round(12-zeitdifferenz-zeitgleichung-(self.lng/15)+self.tz,2)
        untergang = round(12+zeitdifferenz-zeitgleichung-(self.lng/15)+self.tz,2)
        cur_time = date.hour + date.minute/60
        #print("Sonnenuntergangszeit: " + str(untergang+1) + "; Sonnenaufgangszeit: " +str(aufgang-0.5) + " Aktuelle Zeit: "+ str(cur_time))
        if (cur_time > untergang-0.5 or cur_time < aufgang):
            return True
        else:
            return False
            
    def run(self):
        print("Starting Device detection.")
        at_home = False
        lights_on = False
        phones = [Phone('XX:XX:XX:XX:XX:XX',2,'philipp')]#,Phone('XX:XX:XX:XX:XX:XX',2,'kim')]
        trigger = {'philipp':False,'kim':False}
        names_at_home = []
        _count = 0
        while (self.led.stop.value != 1):
            names_at_home = {'philipp':0}#,'kim':0}
            for pho in phones:
                if pho.ping(): #Pinning Phone
                    names_at_home[pho.get_name()] = pho.get_time()
                else:
                    del names_at_home[pho.get_name()]
                    trigger[pho.get_name()]=False
            print(names_at_home)
            if len(names_at_home.keys())==0: #Checks how many phones are in range
                if _count == 20:
                    _count = 0
                    if at_home:
                        if self.rpc.gets():
                            self.blue.send("42&alles_aus") #turns all of includes all PCs
                        else:
                            self.blue.send("42&standby") # just turns of the lights and the speach
                        at_home = False
                    self.signal.emit(False) #Sends Signal to QT interface
                    if lights_on:
                        lights_on = False    
                _count = _count + 1   
            else:
                _count = 0
                if at_home:
                    for name in names_at_home.keys():
                        if names_at_home[name] == 30 and not trigger[name]:
                            print(name + " comes home")
                            self.blue.send("42&heim_kommt_"+ str(name))
                            trigger[name]= True
                            break
                if not at_home:
                    if len(names_at_home.keys())==1:
                        name = list(names_at_home.keys())[0]
                        self.blue.send("10&sag_hallo_zu_"+str(name))
                        print(names_at_home.keys(), " is at home")
                        trigger[name] = True
                    else:
                        for name in names_at_home.keys():
                             trigger[name] = True
                        self.blue.send("10&sag_hallo")
                        print(names_at_home.keys() ," is at home")
                    at_home = True               
                if not lights_on and self.sunstate():
                    lights_on = True
                    self.signal.emit(True)
            sleep(10*len(names_at_home.keys())+6) #Sleeptime to the next ping (let the Networkinterface have a quick chill)
        print("AtHome Thread ended")

class WebServer(QThread):
    #### A simple Webserver to fetch the http requests
    signal = pyqtSignal(str,name="cmd")
    def __init__(self, port=0000, led = NewLED((0,0,0),0)):
        QThread.__init__(self)
        self.led = led
        self.host = 'XXX.XXX.X.XXX' #socket.gethostname().split('.')[0] # Default to any avialable network interface
        self.port = port

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.bind((self.host, self.port))
            print("Server started on port {port}.".format(port=self.port))
        except Exception:
            print("Error: Could not bind to port {port}".format(port=self.port))
            sys.exit(1)
        self.socket.listen(5)
        print("start listening ...")
        while self.led.stop.value == 0:
            (client, address) = self.socket.accept()
            client.settimeout(5)
            print("Recieved connection from {addr}".format(addr=address))
            threading.Thread(target=self._handle_client, args=(client, address)).start()
        print("Webserver ended.")
        self.socket.shutdown(socket.SHUT_RDWR)
        

    def _handle_client(self, client, address):
        PACKET_SIZE = 1024
        try:
            netdata = client.recv(PACKET_SIZE)
            data = netdata.decode() # Recieve data packet from client and decode
            request_method = data.split(' ')[0]
            if request_method == "GET" or request_method == "HEAD":
                command = data.split(' ')[1]
                print(command)
                it = command.find("set")
            if it != -1:
                self.signal.emit(command) # Sends Networkcommand to QT Interface
            client.sendall('HTTP/1.1 200 OK\n'.encode())
            client.close()
        except Exception as e:
            print(e)
            client.close()