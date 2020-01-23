from multiprocessing import Process , freeze_support
from multiprocessing.sharedctypes import Value, Array
from colorutils import degreetoRGB, color_scale100, Color
import time
import pigpio
import module

pi = pigpio.pi()

class NewLED:
    def __init__(self,pins,pwm):
        color = Color()
        color.hue, color.sat, color.int = 0,0,0
        self.overwrite = Value('i',0)
        self.type = Value('i',-1)
        self.stop = Value('i',0)
        self.color = Array(Color,[color],lock=True)
        self.state = Array(Color,[color],lock=True)
        self.delay = 0.02
        self.speed = Value('i',50)
        self.pins = pins
        self.pwm = pwm
    
    def lock_input(self):
        self.overwrite.value = 1
        print("Locking input.")

    def unlock_input(self):
        self.overwrite.value = 0
        print("Unlocking input.")
        
    def set_color(self,hue, sat, intens):
        self.color[0].hue = hue
        self.color[0].sat = sat
        self.color[0].int = intens

    def get_color(self):
        return (self.color[0])
            
    def get_color_hsi(self): # Hue Saturation Value
        return (self.color[0].hue,self.color[0].sat,self.color[0].int)

    def get_color_rgb(self):
        return (color_scale100(degreetoRGB(100,self.color[0].hue,self.color[0].sat),self.color[0].int))

    def set_state(self,color):
        self.state[0].hue = color.hue
        self.state[0].sat = color.sat
        self.state[0].int = color.int

    def get_state(self):
        return self.state[0]
            
    def get_state_hsi(self):
        return (self.state[0].hue,self.state[0].sat,self.state[0].int)

    def get_state_rgb(self):
        return (color_scale100(degreetoRGB(100,self.state[0].hue,self.state[0].sat),self.state[0].int))
    
    def set_type(self,id):
        self.type.value = id
        print("Mode set to " +str(id))
            
    def set_speed(self,speed):
        self.speed.value = speed
        
led1 = NewLED((12,16,21),pi)
led2 = NewLED((13,26,19),pi)
led3 = NewLED((23,24,18),pi)

def pwm_process(myLED):
    '__init__(< Thread ID, Threadname, colorobject, pwmobject, killobject >)'     
    #this is the thread which is running simultanius to the window
    print("Process started!")
    while(myLED.stop.value != 1): #thread ending object
        # State Selection of the LED-Mode
        if(myLED.type.value == 0):
            module.fading(myLED) #Default mode
        elif (myLED.type.value == 1):
            module.auto(myLED) #Fading through all colors
        elif (myLED.type.value == 2):
            module.pulse(myLED) #Fading through the intensity
        elif (myLED.type.value == 3):
            module.sunrise(myLED) #Fading through sunrise colors
        elif (myLED.overwrite.value != 1):
            time.sleep(0.1) #Idle state
        if (myLED.overwrite.value == 1):
            module.direct(myLED) #Direct Overwrite from the QT Gui
    pi.stop()
    print("Process ended.")
        
process1 = Process(target=pwm_process,args=(led1,))
process2 = Process(target=pwm_process,args=(led2,))
process3 = Process(target=pwm_process,args=(led3,)) 
leds = [led1,led2,led3]