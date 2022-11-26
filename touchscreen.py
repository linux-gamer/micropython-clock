from machine import Pin, SPI, PWM
import time, utime
import os


LCD_DC   = 8
LCD_CS   = 9
LCD_SCK  = 10
LCD_MOSI = 11
LCD_MISO = 12
LCD_BL   = 13
LCD_RST  = 15
TP_CS    = 16
TP_IRQ   = 17

class touch():
    def __init__(self):

        self.cs = Pin(LCD_CS, Pin.OUT)
        self.rst = Pin(LCD_RST, Pin.OUT)
        self.dc = Pin(LCD_DC, Pin.OUT)

        self.tp_cs =Pin(TP_CS, Pin.OUT)
        self.irq = Pin(TP_IRQ, Pin.IN, Pin.PULL_UP)
        
        self.width = 320
        self.height = 240

        self.cs(1)
        self.dc(1)
        self.rst(1)
        self.tp_cs(1)
        self.spi = SPI(1, 60_000_000, sck=Pin(LCD_SCK), mosi=Pin(LCD_MOSI), miso=Pin(LCD_MISO))

    def touch_get(self):
        if self.irq() != 0:
            self.spi = SPI(1, 5_000_000, sck=Pin(LCD_SCK), mosi=Pin(LCD_MOSI), miso=Pin(LCD_MISO))
            self.tp_cs(0)
            X_Point = 0
            Y_Point = 0
            for i in range(0, 3):
                self.spi.write(bytearray([0XD0]))
                Read_date = self.spi.read(2)
                utime.sleep_ms(10)
                X_Point=X_Point+(((Read_date[0]<<8)+Read_date[1])>>3)
                    
                self.spi.write(bytearray([0X90]))
                Read_date = self.spi.read(2)
                Y_Point=Y_Point+(((Read_date[0]<<8)+Read_date[1])>>3)
                
            self.tp_cs(1) 
            self.spi = SPI(1, 60_000_000, sck=Pin(LCD_SCK), mosi=Pin(LCD_MOSI), miso=Pin(LCD_MISO))
            return None
        if self.irq() == 0:
            self.spi = SPI(1, 5_000_000, sck=Pin(LCD_SCK), mosi=Pin(LCD_MOSI), miso=Pin(LCD_MISO))
            self.tp_cs(0)
            X_Point = 0
            Y_Point = 0
            for i in range(0, 3):
                self.spi.write(bytearray([0XD0]))
                Read_date = self.spi.read(2)
                utime.sleep_ms(10)
                X_Point=X_Point+(((Read_date[0]<<8)+Read_date[1])>>3)
                    
                self.spi.write(bytearray([0X90]))
                Read_date = self.spi.read(2)
                Y_Point=Y_Point+(((Read_date[0]<<8)+Read_date[1])>>3)

            X_Point=X_Point/3
            Y_Point=Y_Point/3
                
            self.tp_cs(1) 
            self.spi = SPI(1, 60_000_000, sck=Pin(LCD_SCK), mosi=Pin(LCD_MOSI), miso=Pin(LCD_MISO))
            Result_list = [X_Point, Y_Point]
#            print(X_Point, Y_Point)
            return(Result_list)

#if __name__ == "__main__":
#    while True:
#        get = LCD.touch_get()
#        if get != None:
#            X_touch = int((get[1]-430)*480/3270)
#            Y_touch = 320-int((get[0]-430)*320/3270)
#            print(f"X: {X_touch}, Y: {Y_touch}")
#            time.sleep_ms(100)
#        time.sleep_ms(100)
