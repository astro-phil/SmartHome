import time
from math import copysign, sqrt
        
def stoppins(myLED): #Stop PWM
    print("PWM stopped! ")
    for pin in myLED.pins:
        myLED.pwm.set_PWM_dutycycle(pin,0)

def updateDynDC(led,color): #Update LED DutyCycle
    pins = led.pins
    pi = led.pwm
    led.set_state(color)
    color = led.get_state_rgb()
    for i in range(3):
        pi.set_PWM_dutycycle(pins[i],round((color[i] /255)**2 *255,1))
        
def fading(myLED):
    iscolor = myLED.get_state()
    color = myLED.get_color()
    dcolor = [color.hue-iscolor.hue,color.sat-iscolor.sat,color.int-iscolor.int]
    drange = max(abs(dcolor[0]),abs(dcolor[1]),abs(dcolor[2]))
    if (drange != 0):
        dcolor = [dcolor[0]/drange,dcolor[1]/drange,dcolor[2]/drange]
    i = 0
    while(i<round(drange,0) and myLED.type.value == 0 and myLED.overwrite.value == 0):
        iscolor.hue=(iscolor.hue+dcolor[0])
        iscolor.sat=(iscolor.sat+dcolor[1])
        iscolor.int=(iscolor.int+dcolor[2])
        updateDynDC(myLED,iscolor)
        time.sleep(myLED.delay) 
        i = i+1
    if (myLED.overwrite.value != 1):
        myLED.type.value = 99
        
def auto(myLED):
    color = myLED.get_state()
    while(myLED.type.value == 1 and myLED.overwrite.value == 0):
        if (color.hue > 360):
            color.hue = 0
        color.hue = color.hue+0.1
        time.sleep(float(myLED.speed.value)/2000+0.0001)
        updateDynDC(myLED,color)
        
def pulse(myLED):
    sign = 1
    color = myLED.get_state()
    while(myLED.type.value == 2 and myLED.overwrite.value == 0):
        if (color.int < 0.2):
            sign = 1
        if (color.int > 99.9):
            sign = -1
        color.int = sign * 0.1 + color.int
        updateDynDC(myLED,color)
        time.sleep(float(myLED.speed.value)/2000+0.0001)

def direct(myLED):
    while(myLED.overwrite.value == 1):
        updateDynDC(myLED,myLED.color[0])
        time.sleep(0.05)

def sunrise(myLED):
    print("Sunrise simulation started !")
    color = myLED.get_state()
    for x in range(10000):
        if (myLED.type.value != 3 or myLED.stop.value == 1):
                break
        color.hue = 0+sqrt(x)/3
        color.int = sqrt(x)
        color.sat = 100-50 * (x/10000)**2
        time.sleep(0.05)
        updateDynDC(myLED,color)
    myLED.type.value = 99
        
    