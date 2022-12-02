# Version 2022 Q4

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2018-2020 Peter Hinch

# Initialise hardware and framebuf before importing modules.
from nanoguilib.color_setup import ssd  # Create a display instance
from nanoguilib.nanogui import refresh  # Color LUT is updated now.
from nanoguilib.label import Label
from nanoguilib.dial import Dial, Pointer
refresh(ssd, True)  # Initialise and clear display.

import touchscreen

# Now import other modules
import ujson
import secrets
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
from machine import Pin, SPI, PWM
import gc

# Font for CWriter
import nanoguilib.freesans20 as freesans20
import nanoguilib.arial10 as arial10
from nanoguilib.colors import *

ssid = secrets.wlan_ssid
pwd = secrets.wlan_pwd

lat = secrets.lat
lon = secrets.lon

appid = secrets.openweathermap_api_key
request_url = f"https://api.openweathermap.org//data/2.5/weather?lat={lat}&lon={lon}&appid={appid}&lang=DE"

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    log = Label(wri, 150, 20, 50)
    tries = 20
    while tries >0:
        tries -=1
        wlan.connect(ssid, pwd)
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
            log.value(f'Status = {stat}')
            refresh(ssd)
#            print(stat)
        log.value("")
    
def clock():
    gc.collect()
    
    uv = lambda phi : cmath.rect(1, phi)  # Return a unit vector of phase phi
    pi = cmath.pi
    days = (' Montag', 'Dienstag', ' Mittwoch', 'Donnerstag', ' Freitag', ' Samstag', ' Sonntag')
    months = ('Jan', 'Feb', 'Maerz', 'April', 'Mai', 'Juni', 'Juli', 'Aug', 'Sept', 'Okt', 'Nov', 'Dez')

    # Instantiate displayable objects
    weather_display = Label(wri, 5, 5, 10)
    temp_display = Label(wri, 50, 5, 10)
    dial = Dial(wri, 80, 28, height = 180, ticks = 12, bdcolor=BLACK, label=120, pip=False)  # Border in fg color
    cal = Label(wri, 298, 10, 10)
    lbltim = Label(wri, 270, 60, 35)
    x_y = Label(wri, 50, 5, 35)
    hrs = Pointer(dial)
    mins = Pointer(dial)
    secs = Pointer(dial)

    hstart = 0 + 0.7j  # Pointer lengths and position at top
    mstart = 0 + 0.87j
    sstart = 0 + 0.90j
    
    ntptime.settime()
    
    seconds = 0
    timeoffset = 0
    
    LCD = touchscreen.touch()
    
    while True:
        get = LCD.touch_get()
        if get != None:
            Y_touch = int((get[1]-430)*320/3270)
            X_touch = 240-int((get[0]-430)*240/3270)
            if X_touch < 0:
                X_touch = 0
            if Y_touch < 0:
                Y_touch = 0
            if X_touch > 240:
                X_touch = 240
            if Y_touch > 320:
                Y_touch = 320
#            print(f"X: {X_touch}, Y: {Y_touch}")
            x_y.value(f"X: {X_touch}, Y: {Y_touch}")
            refresh(ssd)
            utime.sleep_ms(100)
            
            ssd.rect(5, 50, 140, 80, BLACK, True)
            x_y.value(f"X: {X_touch}, Y: {Y_touch}")
        else:
            ssd.rect(5, 50, 140, 80, BLACK, True)
            utime.sleep_ms(100)
            
        if seconds == 0:
            url = request_url
            _, _, host, path = url.split('/', 3)
            addr = socket.getaddrinfo(host, 80)[0][-1]
            s = socket.socket()
            s.connect(addr)
            s.send(b'GET /%s HTTP/1.0\r\n\r\n' % (path))
            while True:
                data = s.read()
                if data:
                    data_new = str(data, 'utf8')
                    _, data = data_new.split("{", 1)
                    data = ujson.loads("{" + data)  
    
                    timeoffset = int(data["timezone"]) // 3600

                    weather_description = data["weather"][0]["description"]
                    weather_temp = round(data["main"]["temp"] - 273.15, 1)
                    
                    weather_decsription_display = f"Wetter:\n {weather_description}."
                    weather_temp_display = f"Temp: {weather_temp} Grad C."
                else:
                    break
            s.close()
            seconds = 1200
        
        t = utime.localtime()
        
        end_of_the_month = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        if t[0] % 4 == 0 and t[0] % 100 != 0:
            end_of_the_month = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        
        date = t[2]
        day = days[t[6] % 7]
        month = months[t[1] - 1]
        year = t[0]
        
        if (t[3] + timeoffset) >= 24:
            date = date + 1
            day = days[(t[6] + 1) % 7]
            if date >= end_of_the_month[t[1] - 1]:
                month = months[t[1]] # Don't use + 1 because arrays (tuples) begin with zero.
                date = 1
                if t[1] == 12:
                    year = t[0] + 1
                
        if (t[3] + timeoffset) < 0:
            date = date - 1
            day = days[(t[6] - 1) % 7]
            if date <= 0:
                month = months[t[1] - 1]
                date = end_of_the_month[t[1] - 1]
                if t[1] == 1:
                    year = t[0] - 1
        
        hrs.value(hstart * uv(-(t[3]+timeoffset)*pi/6 - t[4]*pi/360), WHITE)
        mins.value(mstart * uv(-t[4] * pi/30), WHITE)
        secs.value(sstart * uv(-t[5] * pi/30), RED)
        ssd.rect(0, 0, 200, 50, BLACK, True)
        weather_display.value(f"{weather_decsription_display}", BLACK, WHITE)
        temp_display.value(f"{weather_temp_display}", BLACK, WHITE)
        lbltim.value(f'{(t[3] + timeoffset) % 24:02d}:{t[4]:02d}:{t[5]:02d} UHR', BLACK, WHITE)
        cal.value(f'{day} {date}. {month} {year}', BLACK, WHITE)
        refresh(ssd)
        seconds -= 1
      
# Instantiate CWriter
CWriter.set_textpos(ssd, 0, 0)  # In case previous tests have altered it
wri = CWriter(ssd, freesans20, GREY, BLACK)  # Report on fast mode. Or use verbose=False
wri.set_clip(True, True, False)

wri2 = CWriter(ssd, arial10, GREY, BLACK)
wri2.set_clip(True, True, False)

connect()
clock()

