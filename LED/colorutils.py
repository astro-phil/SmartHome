from ctypes import Structure, c_double

class Color(Structure):
    _fields_ = [('hue',c_double),('sat',c_double),('int',c_double)]

def degreetoRGB(rad, phi , r):
        'getcolorRGB(<(radian, angle)>) 2-tuple'
        if(r>rad):
            r=rad
            #limits the input radian to the maxradian of the circle
              
        #Red colorsection
        if(phi<120 or phi>240):
            if(phi>240 and phi<300):
                red = 255*((phi-240)/60) #linear increase
            if(phi>60 and phi<120):
                red = 255*((120-phi)/60) #linear decrease
            if(phi<=60 or phi>=300):
                red = 255   #static value
        else:
            red = 0 # out of range
        #Blue colorsection               
        if(phi>0 and phi<240):
            if(phi>0 and phi<60):
                green = 255*((phi)/60)
            if(phi>180 and phi<240):
                green = 255*((240-phi)/60)
            if(phi<=180 and phi>=60):
                green = 255             
        else:
            green = 0
        # Green colorsection               
        if(phi>120 and phi<360):
            if(phi>120 and phi<180):
                blue = 255*((phi-120)/60)
            if(phi>300 and phi<360):
                blue = 255*((360-phi)/60)
            if(phi<=300 and phi>=180):
                blue = 255   
        else:
            blue = 0
        red = (255-red)*((rad-r)/rad) + red
        blue = (255-blue)*((rad-r)/rad) + blue
        green = (255-green)*((rad-r)/rad) + green
        #by approching the centre more of the other values are added
        
        return [red, green, blue] #returns 3-tuple with the color values

def color_scale100(color,scale):
    red = int(round((scale * color[0])/100))
    green = int(round((scale * color[1])/100))
    blue = int(round((scale * color[2])/100))
    return [red,green,blue]
    