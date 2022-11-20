# aclock.py Test/demo program for nanogui
# Orinally for ssd1351-based OLED displays but runs on most displays
# Adafruit 1.5" 128*128 OLED display: https://www.adafruit.com/product/1431
# Adafruit 1.27" 128*96 display https://www.adafruit.com/product/1673

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2018-2020 Peter Hinch

# Initialise hardware and framebuf before importing modules.
from nanoguilib.color_setup import ssd  # Create a display instance
from nanoguilib.nanogui import refresh  # Color LUT is updated now.
from nanoguilib.label import Label
from nanoguilib.dial import Dial, Pointer
refresh(ssd, True)  # Initialise and clear display.

# Now import other modules
import ujson
import cmath
import ntptime
import network
import utime
import urequests
from nanoguilib.writer import CWriter
import uasyncio as asyncio
import network
import socket
import machine
import gc

# Font for CWriter
import nanoguilib.freesans20 as freesans20
import nanoguilib.arial10 as arial10
from nanoguilib.colors import *

ssid = "##"
pwd = "##"

request_url = f"https://api.openweathermap.org//data/2.5/weather?lat=##&lon=##&appid=##"

#display_temp = Label()

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    log = Label(wri, 150, 20, 50)
    tries = 20
    while tries >0:
        tries -=1
        wlan.connect(ssid, pwd)
 #       utime.sleep(1)
        stat = wlan.status()
        while stat == network.STAT_CONNECTING:
            log.value('Verbinde .  ')
            refresh(ssd)
            utime.sleep(0.1)
            log.value("Verbinde ..   ")
            refresh(ssd)
            utime.sleep(0.1)
            log.value("Verbinde ...")
            refresh(ssd)
            utime.sleep(0.1)
            stat = wlan.status()
        if stat == network.STAT_GOT_IP:
            tries = 0
            
            log.value("Verbunden!", BLACK, WHITE)
            refresh(ssd)
            status = wlan.ifconfig()
            print( f"Ip = {status[0]}")
        if stat == network.STAT_WRONG_PASSWORD:
            print( 'wrong password')
        if stat == network.STAT_NO_AP_FOUND:
            print( 'NO_AP_FOUND')
        else:
            log.value(f'status={stat}')
            refresh(ssd)
#            print(stat)
        log.value("")
    
def aclock():
    gc.collect()
    
    uv = lambda phi : cmath.rect(1, phi)  # Return a unit vector of phase phi
    pi = cmath.pi
    days = (' Montag', 'Dienstag', ' Mittwoch', 'Donnerstag', ' Freitag', ' Samstag',
            ' Sonntag')
    months = ('Jan', 'Feb', 'Maerz', 'April', 'Mai', 'Juni', 'Juli',
              'Aug', 'Sept', 'Okt', 'Nov', 'Dez')

    # Instantiate displayable objects
    weather_display = Label(wri2, 5, 5, 10)
    temp_display = Label(wri, 30, 5, 10)
    dial = Dial(wri, 80, 28, height = 180, ticks = 12, bdcolor=BLACK, label=120, pip=False)  # Border in fg color
    cal = Label(wri, 298, 10, 10)
    lbltim = Label(wri, 270, 60, 35)
    hrs = Pointer(dial)
    mins = Pointer(dial)
    secs = Pointer(dial)

    hstart = 0 + 0.7j  # Pointer lengths and position at top
    mstart = 0 + 0.87j
    sstart = 0 + 0.90j
    
    ntptime.settime()
    
    weather_decsription_display = ""
    weather_temp_display = ""
    
    seconds = 10
    timeoffset = 0
    
    while True:
        if seconds == 0:
            url = request_url
            _, _, host, path = url.split('/', 3)
            addr = socket.getaddrinfo(host, 80)[0][-1]
            s = socket.socket()
            s.connect(addr)
            s.send(b'GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host))
            while True:
                data = s.read(1500)
                if data:
                    data_new = str(data, 'utf8')
                    i = 300
                    while data_new[i] != "{":
                        i += 1
                    data = data_new[i:]
                    response = ujson.loads(data)  
                    weather_data = response
    

                    timeoffset = response["timezone"]
                    timeoffset = int(timeoffset / 3600)

                    weather_description = weather_data["weather"][0]["description"]
                    if weather_description == "broken clouds":
                        weather_description = "leicht bewoelkt"
                    if weather_description == "light rain":
                        weather_description = "leicht regnerisch"
                    if weather_description == "rain":
                        weather_description = "regnerisch"
                    if weather_description == "modeate rain":
                        weather_description = "maessig regnerisch"
                    if weather_description == "scattered clouds":
                        weather_description = "aufgelockert bewoelkt"
                    if weather_description == "overcast clouds":
                        weather_description = "bedeckt bewoelkt"
                    if weather_description == "snow":
                        weather_description = "Schnee"
                        weather_description_display = f"Es schneit."
                    if weather_description == "few clouds":
                        weather_description = "etwas bewoelkt"
                    if weather_description == "clear sky":
                        weather_description = "klarer Himmel"

                    weather_temp = round(weather_data["main"]["temp"] - 273.15, 1)
                    
                    weather_description_display = ""
                    weather_temp_display = ""
                    
                    weather_decsription_display = f"Es ist {weather_description}."
                    weather_temp_display = f"Temp: {weather_temp} Grad C."
                else:
                    break
            s.close()
            seconds = 6000
        
        t = utime.localtime()
        hrs.value(hstart * uv(-(t[3]+timeoffset)*pi/6 - t[4]*pi/360), WHITE)
        mins.value(mstart * uv(-t[4] * pi/30), WHITE)
        secs.value(sstart * uv(-t[5] * pi/30), RED)
        ssd.rect(0, 0, 200, 50, BLACK, True)
        weather_display.value(f"{weather_decsription_display}", BLACK, WHITE)
        temp_display.value(f"{weather_temp_display}", BLACK, WHITE)
        lbltim.value(f'{t[3]+timeoffset:02d}:{t[4]:02d}:{t[5]:02d} UHR', BLACK, WHITE)
        cal.value(f'{days[t[6]]} {t[2]}. {months[t[1] - 1]} {t[0]}', BLACK, WHITE)
        refresh(ssd)
        seconds -= 1
        utime.sleep_ms(10)
      
# Instantiate CWriter
CWriter.set_textpos(ssd, 0, 0)  # In case previous tests have altered it
wri = CWriter(ssd, freesans20, GREY, BLACK)  # Report on fast mode. Or use verbose=False
wri.set_clip(True, True, False)

wri2 = CWriter(ssd, arial10, GREY, BLACK)
wri2.set_clip(True, True, False)

connect()
aclock()
