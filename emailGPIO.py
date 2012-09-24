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
output.

Based heavily on example code here:
http://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/

#   ________Pinout______
#   GPIO #      Function
#   21          Enable (Active low)
#   22          Switch Input
#   10          Controller           
#   9           Lights
#   11          Backlight
#   18          LCD 18
#   23          LCD 13
#   24          LCD 12
#   25 `        LCD 11
#   8           LCD 6
#   7           LCD 4
'''

import RPi.GPIO as GPIO
import time
import imaplib
import email
import sys
import ConfigParser
import smtplib
import os
import lcd as lcd


class Configuration() :
    def __init__(self) :
        self.configFile  = ConfigParser.SafeConfigParser()
        self.configFile.read('emailGPIO.cfg')
        self. whiteList = {}
        self.whiteList = self.configFile.get('Email', 'WhiteList').split(' ')
        self.sleepTime = self.configFile.getint('Email', 'Interval')

        self.backlightPin = self.configFile.getint('Hardware', 'Backlight')
        self.enablePin = self.configFile.getint('Hardware', 'Enable')
        self.inputPin = self.configFile.getint('Hardware', 'Input')

        self.speak = self.configFile.get('Configuration', 'Speak')
        self.verbose = self.configFile.get('Configuration', 'Verbose')
        self.approvedSubject = self.configFile.get('Email', 'Subject')

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.backlightPin, GPIO.OUT)
        GPIO.setup(self.enablePin, GPIO.OUT)

        GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
        GPIO.setup(lcd.LCD_E, GPIO.OUT)  # E
        GPIO.setup(lcd.LCD_RS, GPIO.OUT) # RS
        GPIO.setup(lcd.LCD_D4, GPIO.OUT) # DB4
        GPIO.setup(lcd.LCD_D5, GPIO.OUT) # DB5
        GPIO.setup(lcd.LCD_D6, GPIO.OUT) # DB6
        GPIO.setup(lcd.LCD_D7, GPIO.OUT) # DB7

        GPIO.output(self.enablePin, False)
        GPIO.output(self.backlightPin, False)

        self.on = True
        self.off = False
        
sentenceQue = []

state = 'off'
config = Configuration()

login = sys.argv[1]
password = sys.argv[2]

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(login, password)

def show(output, say=True, line=1) :    
    if config.verbose :
        print output
        
    if config.speak and say:
        a = os.system("echo " + output + " | festival --tts")


def show_lcd(message, line=1) :
    if line==1: line = lcd.LCD_LINE_1
    if line==2: line = lcd.LCD_LINE_2
    lcd.lcd_byte(line, lcd.LCD_CMD)
    lcd.lcd_string(message)

GPIO.output(config.backlightPin, True)
show_lcd("Email service")
show_lcd("starting...", line=2)
show('Email service started')

def sendEmail(recipient, subject, message) :
    global login
    global password    
    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(login, password)
    header = 'To:' + recipient + '\n' + 'From: ' + login + '\n' + 'Subject: ' + subject+ ' \n'
    msg = header + '\n '+ message + '\n\n'
    if config.verbose : show('Sending to ' + recipient)
    smtpserver.sendmail(login, recipient, msg)

def get_sender(email_message) :
    sender = email.utils.parseaddr(email_message['From'])    
    name = sender[0]
    addr = sender[1]
    return name, addr   


def get_first_text_block(email_message_instance):
        maintype = email_message_instance.get_content_maintype()
        if maintype == 'multipart':
            for part in email_message_instance.get_payload():
                if part.get_content_maintype() == 'text':
                    return part.get_payload()

        elif maintype == 'text':
            return email_message_instance.get_payload()

if __name__ == '__main__' :
    GPIO.output(config.backlightPin, False)
    lcd.lcd_init()
    time.sleep(1)
    while True:
        show_lcd('', line=1)
        show_lcd('', line=2)
        show('Checking email...', say=False)
        show_lcd("Checking email", line=1)
        #show_lcd(" ", line=2)
        
        try :
            mail.list()
            mail.select('inbox')
            result, data = mail.uid('search', None, "(UNSEEN)")    
            if data[0] != '':        
                latest_email_uid = data[0].split()[-1]
                result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
                raw_email = data[0][1]   
                email_message = email.message_from_string(raw_email)
                name, sender = get_sender(email_message)
                subj = email.utils.parseaddr(email_message['Subject'])[1]        
                if sender in config.whiteList and subj.upper() == config.approvedSubject.upper() :
                    GPIO.output(config.backlightPin, True)
                    show_lcd("Command from:")
                    show_lcd(name, line=2)                    
                    show('Command received from ' + name)
                    text = get_first_text_block(email_message)       
                        
                    if 'on' in text :
                        show_lcd("ON command")
                        show('Output is now on')
                        state = 'on'                        

                    if 'off' in text :
                        show_lcd("OFF command")
                        show('Output is now off')
                        state = 'off'                            
                                           

                    if 'pulse' in text :                 
                        show('Pulsing output')
                        GPIO.output(backlightPinoutPin, False)
                        time.sleep(1)
                        GPIO.output(backlightPinoutPin, True)
                        time.sleep(1)
                        GPIO.output(backlightPinoutPin, False)
                        state = 'off'

                    if not 'noack' in text or 'status' in text:
                        if 'status' in text :
                            show("Status was requested. Pin state is " + state)
                        t = 'Pin state is ' + str(state)
                        sendEmail(sender, 'Status report', t)

        

        except Exception, detail :
            print "ERROR: " + str(detail)
        GPIO.output(config.backlightPin, False)
        if config.verbose :    
            show("Sleeping for " + str(config.sleepTime) + " seconds", say=False)
        show_lcd("Sleeping for ",line=1 )
        show_lcd(str(config.sleepTime) + " seconds", line=2)
        time.sleep(config.sleepTime)
    



