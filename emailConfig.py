import ConfigParser
import RPi.GPIO as GPIO
import lcd

class Configuration() :
    def __init__(self) :
        '''
        #   ________Pinout______
        #   GPIO #      Function
        #   21          Enable (Active low)
        #   22          Switch Input
        #   10          Output           
        #   9           Lights
        #   11          Backlight
        #   18          LCD 18
        #   23          LCD 13
        #   24          LCD 12
        #   25 `        LCD 11
        #   8           LCD 6
        #   7           LCD 4
        '''
        self.configFile  = ConfigParser.SafeConfigParser()
        self.configFile.read('emailGPIO.cfg')
        self. whiteList = {}
        self.whiteList = self.configFile.get('Email', 'WhiteList').split(' ')
        self.sleepTime = self.configFile.getint('Email', 'Interval')
        self.approvedSubject = self.configFile.get('Email', 'Subject')

        self.backlightPin = self.configFile.getint('Hardware', 'Backlight')
        self.enablePin = self.configFile.getint('Hardware', 'Enable')
        self.outputPin = self.configFile.getint('Hardware', 'Output')
        self.lightsPin = self.configFile.getint('Hardware', 'Lights')
        self.inputPin = self.configFile.getint('Hardware', 'Input')

        lcd.LCD_E = self.configFile.getint('Hardware', 'LCD_E')
        lcd.LCD_RS = self.configFile.getint('Hardware', 'LCD_RS')
        lcd.LCD_D4 = self.configFile.getint('Hardware', 'LCD_D4')
        lcd.LCD_D5 = self.configFile.getint('Hardware', 'LCD_D5')
        lcd.LCD_D6 = self.configFile.getint('Hardware', 'LCD_D6')
        lcd.LCD_D7 = self.configFile.getint('Hardware', 'LCD_D7')

        s = self.configFile.get('Configuration', 'Speak')
        if s.lower() == 'true' : self.speak = True
        else : self.speak = False
        self.verbose = self.configFile.get('Configuration', 'Verbose')
        self.displayTime = self.configFile.getint('Configuration', 'DisplayTime')

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.backlightPin, GPIO.OUT)
        GPIO.setup(self.enablePin, GPIO.OUT)
        GPIO.setup(self.outputPin, GPIO.OUT)
        GPIO.setup(self.lightsPin, GPIO.OUT)
        GPIO.setup(self.inputPin, GPIO.IN)        

        GPIO.setup(lcd.LCD_E, GPIO.OUT)  # E
        GPIO.setup(lcd.LCD_RS, GPIO.OUT) # RS
        GPIO.setup(lcd.LCD_D4, GPIO.OUT) # DB4
        GPIO.setup(lcd.LCD_D5, GPIO.OUT) # DB5
        GPIO.setup(lcd.LCD_D6, GPIO.OUT) # DB6
        GPIO.setup(lcd.LCD_D7, GPIO.OUT) # DB7

        GPIO.output(self.enablePin, False)
        GPIO.output(self.backlightPin, False)
        GPIO.output(self.lightsPin, False)
        GPIO.output(self.outputPin, False)
