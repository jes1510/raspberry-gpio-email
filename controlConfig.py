import ConfigParser
import RPi.GPIO as GPIO
#import lcd

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
        #   18          LCD 14
        #   23          LCD 13
        #   24          LCD 12
        #   25 `        LCD 11
        #   8           LCD 6
        #   7           LCD 4
        '''
        self.configFile  = ConfigParser.SafeConfigParser()
        self.configFile.read('control.cfg')
        self. whiteList = {}
        self.whiteList = self.configFile.get('Email', 'WhiteList').split(' ')
        self.sleepTime = self.configFile.getint('Email', 'Interval')
        self.approvedSubject = self.configFile.get('Email', 'Subject')

        self.backlightPin = self.configFile.getint('Hardware', 'Backlight')
        self.enablePin = self.configFile.getint('Hardware', 'Enable')
        self.outputPin = self.configFile.getint('Hardware', 'Output')
        self.lightsPin = self.configFile.getint('Hardware', 'Lights')
        self.inputPin = self.configFile.getint('Hardware', 'Input')

        self.LCD_E = self.configFile.getint('Hardware', 'LCD_E')
        self.LCD_RS = self.configFile.getint('Hardware', 'LCD_RS')
        self.LCD_D4 = self.configFile.getint('Hardware', 'LCD_D4')
        self.LCD_D5 = self.configFile.getint('Hardware', 'LCD_D5')
        self.LCD_D6 = self.configFile.getint('Hardware', 'LCD_D6')
        self.LCD_D7 = self.configFile.getint('Hardware', 'LCD_D7')

        s = self.configFile.get('Configuration', 'Speak')
        if s.lower() == 'true' : self.speak = True
        else : self.speak = False
        self.verbose = self.configFile.get('Configuration', 'Verbose')
        self.displayTime = self.configFile.getint('Configuration', 'DisplayTime')


