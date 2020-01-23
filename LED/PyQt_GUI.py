#!/usr/bin/python3

import sys
from multiprocessing import freeze_support
from new_gui import QtWidgets, Ui_MainWindow, QtGui
from PyQt5.QtCore import QThread, pyqtSignal, QTime, QTimer
from LED import led1,led2,led3 , process1, process2, process3, NewLED
from time import sleep, localtime
from http.server import BaseHTTPRequestHandler, HTTPServer
from Network import WebServer, Interface, AtHome, Pi2Pi, RemotePC
from requests import get

face = 0 # current face
update_state = True # Keep the UI updateted
alarm_time = ["06:00","08:00","08:00","08:00","06:00","10:00","10:00","23:00"] # Default alarm times
alarm_activ = [False,False,False,False,False,False,False] # Default alarm state

if __name__ == '__main__':
    freeze_support()
    process1.start() # Starting LED process
    process2.start()
    process3.start()

    # Laoding all necessary objects
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    pi2pi = Pi2Pi()
    rpc = RemotePC()

    # Organizing buttons
    color_dails = (ui.color_1,ui.color_2,ui.color_3)
    bright_dails = (ui.bright_1,ui.bright_2,ui.bright_3)
    bright_digits = (ui.nbright_1,ui.nbright_2,ui.nbright_3)
    satur_dails = (ui.satur_1,ui.satur_2,ui.satur_3)
    satur_digits = (ui.nsatur_1,ui.nsatur_2,ui.nsatur_3)
    speed_dails = (ui.speed_1,ui.speed_2,ui.speed_3)
    auto_buttons = (ui.bauto_1,ui.bauto_2,ui.bauto_3)
    pulse_buttons = (ui.bpulse_1,ui.bpulse_2,ui.bpulse_3)
    led_R_stats = (ui.LED_1_R,ui.LED_2_R,ui.LED_3_R)
    led_G_stats = (ui.LED_1_G,ui.LED_2_G,ui.LED_3_G)
    led_B_stats = (ui.LED_1_B,ui.LED_2_B,ui.LED_3_B)
    blacks = (ui.black_1,ui.black_2,ui.black_3)
    whites = (ui.white_1,ui.white_2,ui.white_3)
    reds = (ui.red_1,ui.red_2,ui.red_3)
    greens = (ui.green_1,ui.green_2,ui.green_3)
    blues = (ui.blue_1,ui.blue_2,ui.blue_3)
    yellows = (ui.yellow_1,ui.yellow_2,ui.yellow_3)
    pinks = (ui.pink_1,ui.pink_2,ui.pink_3)
    purples = (ui.purple_1,ui.purple_2,ui.purple_3)
    oranges = (ui.orange_1,ui.orange_2,ui.orange_3)
    cyans = (ui.cyan_1,ui.cyan_2,ui.cyan_3)
    leds = (led1,led2,led3)

    ### Exit Button ####

    def exit():
        MainWindow.destroy()
        for led in leds:
            led.set_color(0,0,0)
            led.type.value = 0
        sleep(1)
        for led in leds:
            led.stop.value = 1
        sys.exit()
    ui.exit.pressed.connect(exit)

    ### Current Tabbar ###

    def tabBar(id):
        global update_state
        if id < 3:
            global face
            face = id
            update_state = True
        else:
            update_state = False
        return
    ui.tabs.tabBarClicked.connect(tabBar)

    ### Dailsection ###############

    def dail_pressed():
        leds[face].lock_input() 
        return

    def dail_released():
        leds[face].unlock_input()
        return

    ### Brightness Dail
    def color_dail():
        value =  bright_dails[face].value()
        bright_digits[face].display(value)
        leds[face].color[0].int = value
        value =  satur_dails[face].value()
        satur_digits[face].display(value)
        leds[face].color[0].sat = value
        value = color_dails[face].value()+180
        if value > 360:
            leds[face].color[0].hue = value - 360
        else:
            leds[face].color[0].hue = value
        return

    for bright in bright_dails: # Connecting all the dails
        bright.sliderPressed.connect(dail_pressed)
        bright.sliderMoved.connect(color_dail)
        bright.sliderReleased.connect(dail_released)
    for satur in satur_dails:
        satur.sliderPressed.connect(dail_pressed)
        satur.sliderMoved.connect(color_dail)
        satur.sliderReleased.connect(dail_released)
    for color in color_dails:
        color.sliderPressed.connect(dail_pressed)
        color.sliderMoved.connect(color_dail)
        color.sliderReleased.connect(dail_released)

    ### Speed Dail
    def speed_dail():
        leds[face].set_speed(speed_dails[face].value())
        return
    
    for speed in speed_dails:
        speed.sliderMoved.connect(speed_dail)

    ### Mode Buttons
    def auto_mode(checked):
        pulse_buttons[face].setChecked(False)
        if checked:
            leds[face].set_type(1)
        else:
            leds[face].set_type(99)
        return
    for auto in auto_buttons:
        auto.toggled.connect(auto_mode)

    def pulse_mode(checked):
        auto_buttons[face].setChecked(False)
        if checked:
            leds[face].set_type(2)
        else:
            leds[face].set_type(99)
        return
    for pulse in pulse_buttons:
        pulse.toggled.connect(pulse_mode)

    ### Color Buttons
    
    def white():
        leds[face].set_color(30,50,100)
        leds[face].set_type(0)
        return
    for bwhite in whites:
        bwhite.pressed.connect(white)
    def black():
        leds[face].set_color(0,0,0)
        leds[face].set_type(0)
        return
    for bblack in blacks:
        bblack.pressed.connect(black)
    def red():
        leds[face].set_color(0,100,100)
        leds[face].set_type(0)
        return
    for bred in reds:
        bred.pressed.connect(red)
    def blue():
        leds[face].set_color(240,100,100)
        leds[face].set_type(0)
        return
    for bblue in blues:
        bblue.pressed.connect(blue)
    def green():
        leds[face].set_color(120,100,100)
        leds[face].set_type(0)
        return
    for bgreen in greens:
        bgreen.pressed.connect(green)
    def orange():
        leds[face].set_color(30,100,100)
        leds[face].set_type(0)
        return
    for borange in oranges:
        borange.pressed.connect(orange)
    def pink():
        leds[face].set_color(340,100,100)
        leds[face].set_type(0)
        return
    for bpink in pinks:
        bpink.pressed.connect(pink)
    def purple():
        leds[face].set_color(300,100,100)
        leds[face].set_type(0)
        return
    for bpurple in purples:
        bpurple.pressed.connect(purple)
    def cyan():
        leds[face].set_color(180,100,100)
        leds[face].set_type(0)
        return
    for bcyan in cyans:
        bcyan.pressed.connect(cyan)
    def yellow():
        leds[face].set_color(60,100,100)
        leds[face].set_type(0)
        return
    for byellow in yellows:
        byellow.pressed.connect(yellow)

    ### Synced Buttons ###

    def lights_on():
        for led in leds:
            led.set_color(30,50,100)
            led.set_type(0)
        return

    def lights_off():
        for led in leds:
            led.set_color(0,0,0)
            led.set_type(0)
        return

    def lights_auto():
        for led in leds:
            led.set_type(1)
        return

    def pc_auto(checked):
        rpc.sets(checked)
        return 0

    ui.lon.pressed.connect(lights_on)
    ui.loff.pressed.connect(lights_off)
    ui.auto_2.pressed.connect(lights_auto)
    ui.pc_act.toggled.connect(pc_auto)

    ### Update interface ###

    def update(id):
        if update_state:
            if (leds[face].overwrite.value == 0):
                value = leds[face].state[0].hue - 180
                if value < 0 :
                    color_dails[face].setValue(value+360)
                else:
                    color_dails[face].setValue(value)
                bright_dails[face].setValue(leds[face].state[0].int)
                satur_dails[face].setValue(leds[face].state[0].sat)
                bright_digits[face].display(int(leds[face].state[0].int))
                satur_digits[face].display(int(leds[face].state[0].sat))
            led_R_stats[face].setValue(leds[face].get_state_rgb()[0])
            led_G_stats[face].setValue(leds[face].get_state_rgb()[1])
            led_B_stats[face].setValue(leds[face].get_state_rgb()[2])
            if (leds[face].type.value == 0):
                if pulse_buttons[face].isChecked():
                    pulse_buttons[face].setChecked(False)
                    leds[face].set_type(0)
                if auto_buttons[face].isChecked():
                    auto_buttons[face].setChecked(False)
                    leds[face].set_type(0)
            elif(leds[face].type.value == 1):
                if pulse_buttons[face].isChecked():
                    pulse_buttons[face].setChecked(False)
                    leds[face].set_type(1)
                if not auto_buttons[face].isChecked():
                    auto_buttons[face].setChecked(True)
            elif(leds[face].type.value == 2):
                if auto_buttons[face].isChecked():
                    auto_buttons[face].setChecked(False)
                    leds[face].set_type(2)
                if not pulse_buttons[face].isChecked():
                    pulse_buttons[face].setChecked(True)
        return 0

    faceupdate = QTimer()
    faceupdate.timeout.connect(update) # Connects interface update to a QTimer
    faceupdate.setInterval(100)
    faceupdate.start(1000)

    ### Alarm Section ###
    daytimes = (ui.mon_time,ui.tue_time,ui.wed_time,ui.thu_time,ui.fri_time,ui.wee_time,None,ui.off_time)
    bdays = (ui.bmon,ui.btue,ui.bwed,ui.bthu,ui.bfri,ui.bwee)
    def setmon():
        alarm_time[0]=daytimes[0].dateTime().toString('hh:mm')
        return
    daytimes[0].dateTimeChanged.connect(setmon)
    def settue():
        alarm_time[1]=daytimes[1].dateTime().toString('hh:mm')
        return
    daytimes[1].dateTimeChanged.connect(settue)
    def setwed():
        alarm_time[2]=daytimes[2].dateTime().toString('hh:mm')
        return
    daytimes[2].dateTimeChanged.connect(setwed)
    def setthu():
        alarm_time[3]=daytimes[3].dateTime().toString('hh:mm')
        return
    daytimes[3].dateTimeChanged.connect(setthu)
    def setfri():
        alarm_time[4]=daytimes[4].dateTime().toString('hh:mm')
        return
    daytimes[4].dateTimeChanged.connect(setfri)
    def setwee():
        alarm_time[5]=daytimes[5].dateTime().toString('hh:mm')
        alarm_time[6]=daytimes[5].dateTime().toString('hh:mm')
        return
    daytimes[5].dateTimeChanged.connect(setwee)
    def setoff():
        alarm_time[7]=daytimes[7].dateTime().toString('hh:mm')
        return
    daytimes[7].dateTimeChanged.connect(setoff)

    def setmon_tg(checked):
        print("Alarm Monday state: "+str(checked))
        alarm_activ[0]=checked
        return
    bdays[0].toggled.connect(setmon_tg)
    def settue_tg(checked):
        print("Alarm Tuesday state: "+str(checked))
        alarm_activ[1]=checked
        return
    bdays[1].toggled.connect(settue_tg)
    def setwed_tg(checked):
        print("Alarm Wednesday state: "+str(checked))
        alarm_activ[2]=checked
        return
    bdays[2].toggled.connect(setwed_tg)
    def setthu_tg(checked):
        print("Alarm Thursday state: "+str(checked))
        alarm_activ[3]=checked
        return
    bdays[3].toggled.connect(setthu_tg)
    def setfri_tg(checked):
        print("Alarm Friday state: "+str(checked))
        alarm_activ[4]=checked
        return
    bdays[4].toggled.connect(setfri_tg)
    def setwee_tg(checked):
        print("Alarm Weekend state: "+str(checked))
        alarm_activ[5]=checked
        alarm_activ[6]=checked
        return
    bdays[5].toggled.connect(setwee_tg)

    ### Update Clock ###

    def showTime():
        time = QTime.currentTime()
        day = localtime().tm_wday
        secs = int(time.toString('ss'))
        text = time.toString('hh:mm')
        if (time.second() % 2) == 0:
            text = text[:2] + ' ' + text[3:]
        ui.ntime.display(text)

        if (alarm_time[day]==text and alarm_activ[day] and secs < 2): # Alarms
            print("Wakeupscquence initialized !")
            if ui.snooze.isChecked():
                cmd = '1&sag_nichts' 
            else:
                cmd = '11&sag_guten_morgen' # Wakeupcommand for network
            for led in leds:
                led.set_type(3)
            try:
                pi2pi.send(cmd) # Sends command to the other Raspberry
            except Exception as e:
                print(e)
                print("Could not reach speechnode.")
            return

        if (alarm_time[7]==text and secs < 2): # Autoshutdown
            print("Shuttings down LEDS.")
            if (leds[0].get_color().int + leds[1].get_color().int + leds[2].get_color().int < 4):
                cmd = '99&sag_nichts'
            else:
                cmd = '42&sag_gute_nacht'
            for led in leds:
                led.set_color(0,0,0)
                led.set_type(0)
            try:
                pi2pi.send(cmd)
            except Exception as e:
                print(e)
                print("Could not reach speechnode.")
            return

    timer = QTimer()
    timer.timeout.connect(showTime)
    timer.start(1000)

    ### Network Section ###

    def netcommand(cmd):
        # executing network commands
        if cmd.find("led")!=-1:
            # Splitting the Commend into different parts
            led_it = cmd.find("_led")+len("_led")
            color_it = cmd.find("_color=")+len("_color=")
            mode_it = cmd.find("_mode=")+len("_mode=")
            if led_it > 5 and color_it > 7 and mode_it > 7:
                # String to int
                led_id = int(cmd[led_it])
                hue = int(cmd[color_it:color_it+3])
                sat = int(cmd[color_it+3:color_it+6])
                bit = int(cmd[color_it+6:color_it+9])
                mode = int(cmd[mode_it])
                print(led_id,mode,hue,sat,bit)
                if (mode == 0):
                    if (led_id != 9):
                        leds[led_id].set_color(hue,sat,bit)
                        leds[led_id].set_type(0)
                        return 0
                    else:
                        for x in range(3):
                            leds[x].set_color(hue,sat,bit)
                            leds[x].set_type(0)
                        return 0
                else:
                    if (led_id != 9):
                        if (mode == 1):
                            leds[led_id].set_type(1)
                            return 0
                        if (mode == 2):
                            leds[led_id].set_type(2)
                            return 0
                    else:
                        if (mode == 1):
                            for x in range(3):
                                leds[x].set_type(1)
                            return 0
                        if (mode == 2):
                            for x in range(3):
                                leds[x].set_type(2)
                            return 0
        elif(cmd.find("alarm")!=-1):
            print(cmd)
            # Splitting the Command
            alarm_it = cmd.find("_alarm")+len("_alarm")
            time_it =  cmd.find("_time=")+len("_time=")
            alarm = int(cmd[alarm_it])
            if (cmd.find("off")!=-1):
                alarm_activ[alarm]=False
                bdays[alarm].setChecked(False)
                return 0
            else:
                if (alarm != 7):
                    bdays[alarm].setChecked(True)
                if (alarm == 5):
                    alarm_time[6]=cmd[time_it:time_it+5]
                alarm_time[alarm]=cmd[time_it:time_it+5]
                daytimes[alarm].setTime(QTime(int(cmd[time_it:time_it+2]),int(cmd[time_it+3:time_it+5])))
                return 0
        return -1

    network = WebServer(port=0000,led=leds[0])
    network.signal.connect(netcommand)
    network.start()

    ### Automatic Lights off and on ###

    def auto_lights(state):
        if state and leds[0].get_color().int + leds[1].get_color().int + leds[2].get_color().int < 4:
            lights_on()
        elif not state:
            lights_off()

    blping = AtHome(lng = 0.000, lat = 00.000 ,tz = 1,led = leds[0],blue=pi2pi,rpc = rpc)
    blping.signal.connect(auto_lights)
    blping.start()

    ### Start GUI ###

    #QtGui.QGuiApplication.processEvents()
    MainWindow.showFullScreen()
    #MainWindow.show()
    sys.exit(app.exec_())
