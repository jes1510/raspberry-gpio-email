#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Written by Jesse Merritt 
www.github.com/jes1510 
September 8 , 2012

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/

Toggles GPIO pin based on contents of an email received over IMAP.
The sender must be listed in the 'WhiteList' in the 'Email' section
of the configuration file.  If the 'speak' flag is set in the config
file then festival will be used as an output to actually speak the
output.  All pins and general configuration happens in the emailConfig
module.

Based heavily on example code here:
http://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/

'''
import urllib
import RPi.GPIO as GPIO
import time
import imaplib
import email
import sys
import smtplib
import os
import controlConfig
from datetime import datetime
import lcd as lcd

if sys.platform == 'linux2' :
    import syslog

state = 'off'
config = controlConfig.Configuration()

login = sys.argv[1]
password = sys.argv[2]

GPIO.setmode(GPIO.BCM)
GPIO.setup(config.backlightPin, GPIO.OUT)
GPIO.setup(config.enablePin, GPIO.OUT)
GPIO.setup(config.outputPin, GPIO.OUT)
GPIO.setup(config.lightsPin, GPIO.OUT)
GPIO.setup(config.inputPin, GPIO.IN)
GPIO.setup(config.LCD_RS, GPIO.OUT)
GPIO.setup(config.LCD_E, GPIO.OUT)
GPIO.setup(config.LCD_D4, GPIO.OUT)
GPIO.setup(config.LCD_D5, GPIO.OUT)
GPIO.setup(config.LCD_D6, GPIO.OUT)
GPIO.setup(config.LCD_D7, GPIO.OUT)

GPIO.output(config.enablePin, False)
GPIO.output(config.backlightPin, False)
GPIO.output(config.lightsPin, False)
GPIO.output(config.outputPin, False)

GPIO.output(config.backlightPin, True)

#dataPins = [config.LCD_D4, config.LCD_D5, config.LCD_D6, config.LCD_D7]
#lcd = Adafruit_CharLCD(pin_rs=config.LCD_RS, pin_e=config.LCD_E, pins_db=dataPins)
#lcd.begin(16,1)

lcd.LCD_RS = config.LCD_RS
lcd.LCD_E  = config.LCD_E
lcd.LCD_D4 = config.LCD_D4
lcd.LCD_D5 = config.LCD_D5
lcd.LCD_D6 = config.LCD_D6
lcd.LCD_D7 = config.LCD_D7
lcd.LED_ON = config.backlightPin

lcd.lcd_init()
lcd.message = lcd.lcd_string        # Keeps some compatibility with the Adafruit module

if config.verbose == 'True' :  config.verbose = True
else : config.verbose = False

if config.speak == 'True' : config.speak = True
else : config.speak = False


def log(message) :    
    if config.logFile != 'system' :
        of=open(config.logFile, 'a')        
        of.write(str(datetime.now()) + '\t' + message + '\n')
        of.close()
    
    if config.logFile == 'system' and sys.platform == 'linux2' :        
        syslog.syslog(message)     
    

def leave() :
    log("Exiting")
    sys.exit(0)
        

def timer(seconds) :
    try :
        while seconds > 0 :
            lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
            lcd.message(str(seconds) + " seconds", style=2)
            seconds -= 1
            time.sleep(1)
            
        return 0
    
    except KeyboardInterrupt :
        leave()
        

def speak(output) :   
    if config.speak :
        a = os.system("echo " + output + " | festival --tts")


def show_lcd(message, line=1) :
    if line == 1 :
        lcd.home()
        lcd.message(message)
    if line == 2 :
        lcd.setCursor(1,2)
        lcd.message(message)
        
class Mailmanager() :
    def __init__(self, login, password) :
        self.login = login
        self.password = password

        self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
        self.mail.login(login, password)

    def getMail(self) :
        self.mail.list()
        self.mail.select('inbox')
        result, data = mail.uid('search', None, "(UNSEEN)")    
        if data[0] != '':            
            time.sleep(.1)
            latest_email_uid = data[0].split()[-1]
            result, data = self.mail.uid('fetch', latest_email_uid, '(RFC822)')
            raw_email = data[0][1]   
            message = email.message_from_string(raw_email)
            name, sender = self.get_sender(message)
            subj = email.utils.parseaddr(message['Subject'])[1]
            text = self.getBody(message) 
            return name, sender, subj, text
        
        else :
            return 0, 0, 0, 0

    def stop(self) :
        self.mail.close()
        self.mail.logout()        
        
        
    def sendEmail(self, recipient, subject, message) :           
        smtpserver = smtplib.SMTP("smtp.gmail.com",587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        smtpserver.login(login, password)
        header = 'To:' + recipient + '\n' + 'From: ' + login + '\n' + 'Subject: ' + subject+ ' \n'
        msg = header + '\n '+ message + '\n\n'        
        smtpserver.sendmail(login, recipient, msg)
        smtpserver.quit()

    def get_sender(self,email_message) :
        sender = email.utils.parseaddr(email_message['From'])    
        name = sender[0]
        addr = sender[1]
        return name, addr

    def getBody(self, email_message_instance):
        maintype = email_message_instance.get_content_maintype()
        if maintype == 'multipart':
            for part in email_message_instance.get_payload():
                if part.get_content_maintype() == 'text':
                    return part.get_payload()

        elif maintype == 'text':
            return email_message_instance.get_payload()

        

class Commands() :
    def __init__(self) :
        pass
    
    def _getIP(self):
        whatismyip = 'http://automation.whatismyip.com/n09230945.asp'
        return urllib.urlopen(whatismyip).readlines()[0]

    def ip(self) :
        lcd.home()
        lcd.message("IP Request")
        ip = self._getIP()
        mailmanager.sendEmail(sender, 'IP Info', ip)


    def warn(self, command) :  
        GPIO.output(config.lightsPin, True)
        lcd.home()
        lcd.message(command.capitalize() + " in", style = 2)
        timer(config.warningTime)
        GPIO.output(config.lightsPin, False)

    def openDoor(self) :
        log("Placeholder for Open")
        

    def closeDoor(self) :        
        log("Placeholder for Close")
             
    def on(self) :
        lcd.clear()
        lcd.message("ON command")
        GPIO.output(config.lightsPin, True)        
        time.sleep(config.displayTime)

    def off(self) :    
        lcd.home()       
        lcd.message("OFF command") 
        GPIO.output(config.lightsPin, False)                                  
        time.sleep(config.displayTime)

    def status(self) :         
        lcd.clear()        
        lcd.message("Status request:")
        lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
        lcd.message("Pin is " + str(state))
        

    def readInput(self) :
        pinState = GPIO.input(config.inputPin)
        return pinState


commands = Commands()
mailmanager = Mailmanager(login, password)
mail = mailmanager.mail


if __name__ == '__main__' :
    log("Control Server started\n")
    try :
        state = 'off'
        GPIO.output(config.backlightPin, False)
        lcd.home()
        lcd.message('Message service', style=2)
        lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
        lcd.message('started', style=2)        
        time.sleep(3)
        while True:            
            lcd.clear()
            time.sleep(.1)
            if config.verbose: log('Checking messages...')
            lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
            lcd.message("Checking", style=2)
            lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
            lcd.message("messages", style=2)
            time.sleep(3)
            number = 0
            
            try :
                #raise TypeError("Test Error...")
                name, sender, subj, text = mailmanager.getMail()            
                
                if text :                
                    text = text.strip()
                    text = text.lower()
                    numList = sender.split('.')
                    number = numList[1]
                    try :
                        assert int(number)
                    except :
                        pass                    
                    
                if sender in config.whiteList or number in config.whiteList:                
                    GPIO.output(config.backlightPin, True)
                    lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
                    lcd.message("Command from:")
                    lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
                    lcd.message('\n' + name) 
                    log(text.capitalize() + " command received from " + name)
                    time.sleep(.1)
                    
                    if 'ip' in text :
                        commands.ip()                
                                                        
                    if 'on' in text :                
                        commands.on()
                        state = 'on'               

                    if 'off' in text :
                        commands.off()           
                        state = 'off'

                    if 'open' in text : 
                        state = 'open'
                        commands.warn('open')
                        commands.openDoor()

                    if 'close' in text :
                        state = 'closed' 
                        commands.warn('close')
                        commands.closeDoor()
                        

                    if not 'noack' in text or 'status' in text: 
                        if 'status' in text :
                            commands.status()
                        
                        t = 'Input is ' + str(commands.readInput()) + '\r\nOutput is ' + str(state)  

                        if config.verbose : log('Sending reply to ' + sender)
                        mailmanager.sendEmail(sender, 'Status report', t)
                        time.sleep(config.displayTime)
                    
           # except smtplib.socket.socketerror :
                
                

            except Exception, detail :                
                log("Error: " + str(detail) + '\n')
                           
                lcd.clear()
                lcd.message("Restarting in", style=2)
                try :
                    mailmanager.stop()
                    
                except Exception, detail:
                    #of.write(str(datetime.now()) + "\tError: " + str(detail) + '\n')
                    log("Error: " + str(detail))                  
                    
                    try :
                        timer(config.sleepTime)
                        lcd.clear()
                        lcd.message("Retrying...", style=2)
                        log("Retrying connection")
                        mailmanager.__init__(login, password)
                        time.sleep(3)
                        
                    except :
                        pass
                
            GPIO.output(config.backlightPin, False)
            if config.verbose :    
                log("Sleeping for " + str(config.sleepTime) + " seconds")
                
            lcd.clear()
            time.sleep(.1)
            lcd.message("Sleeping for", style=2)
            timer(config.sleepTime )
    
        
    except KeyboardInterrupt() :
        leave()
                         
    



