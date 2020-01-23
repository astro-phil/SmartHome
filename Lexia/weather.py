import pyowm
from random import randint

class Weather(object):
    def __init__(self,loc = 'ACIITY,XX'):
        self.owm = pyowm.OWM('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX') # Weather API Key
        self.loc = loc

    def get_temp(self,number):
        #### This function converts temperature values into words
        text = []
        if number < -10:
            text.append("under")
            text.append("minus")
            text.append(str(10))
        elif number < 0:
            text.append("minus")
            text.append(str(int(abs(number))))
        elif number > 40:
            text.append("over")
            text.append(str(40))
        else:
            text.append(str(int(abs(number))))
        return text

    def get_wind_num(self,number):
        #### This function converts wind velocity values into words
        text = []
        number = int(round(number * 3.6,0))
        rest = number % 10
        if number > 90:
            text.append("over")
            text.append(str(90))
        elif number > 30 and rest > 0:
            number = number - rest
            text.append("over")
            text.append(str(number))
        else:
            text.append(str(number))
        return text

    def get_weather_now(self):
        #### Reading weather information for current time
        loc = self.owm.weather_at_place('ACITY,XX')
        weather = loc.get_weather()
        state = (weather.get_detailed_status().replace(" ","_"))
        temp = (weather.get_temperature('celsius')['temp'])
        wind = (weather.get_wind()['speed'])
        return state, int(temp) , int(wind)

    def get_weather_today(self):
        #### Reading weatherforecast for today
        fc = self.owm.three_hours_forecast('ACITY,XX')
        f = fc.get_forecast()
        weather_lines= []
        for weather in f:
            weather_lines.append([weather.get_reference_time('iso'),weather.get_detailed_status().replace(" ","_"),weather.get_temperature('celsius')['temp'],weather.get_wind()['speed']])
            if len(weather_lines)>8:
                break
        str_today = weather_lines[0][0][0:10]
        first_state = weather_lines[0][1]
        forcast = [first_state]
        temp_max = (-30,0)
        temp_min = (30,0)
        wind = (0,0)
        for weather in weather_lines: #### Filtering weatherforecast text
            if weather[0].find(str_today)==-1:
                break
            if weather[1]!=first_state:
                forcast.append(int(weather[0][11:13]))
                first_state = weather[1]
                forcast.append(weather[1])
            if temp_max[0] < weather[2]:
                temp_max = (int(round(weather[2],0)),int(weather[0][11:13]))
            if temp_min[0] > weather[2]:
                temp_min = (int(round(weather[2],0)),int(weather[0][11:13]))
            if wind[0] < weather[3]:
                wind = (int(round(weather[3],0)),int(weather[0][11:13]))
        return forcast, (temp_max,temp_min), wind