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

import RPi.GPIO as GPIO
import time
import imaplib
import email
import sys
import smtplib
import os
import controlConfig 
import lcd as lcd

state = 'off'
config = controlConfig.Configuration()

login = sys.argv[1]
password = sys.argv[2]

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(login, password)


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

def show(output, say=True, line=1) :    
    if config.verbose :
        print output
        
    if config.speak and say:
        a = os.system("echo " + output + " | festival --tts")


def show_lcd(message, line=1) :
    if line == 1 :
        lcd.home()
        lcd.message(message)
    if line == 2 :
        lcd.setCursor(1,2)
        lcd.message(message)
        
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
    lcd.home()
    lcd.message("Email service\n")

    lcd.message('Email service started')
    time.sleep(1)
    while True:
        time.sleep(.1)
        lcd.home()
        time.sleep(.1)
        lcd.clear()
        time.sleep(.1)        
        show('Checking email...', say=False)
        lcd.message("Checking email")
        time.sleep(3)
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
                    lcd.message("Command from:")
                    lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
                    lcd.message('\n' + name)                    
                    show('Command received from ' + name)
                    text = get_first_text_block(email_message)       
                        
                    if 'on' in text :
                        #lcd.clear()
                        lcd.home()
                        time.sleep(.1)
                        lcd.message("ON command")                        
                        show('Output is now on')
                        GPIO.output(config.lightsPin, True)
                        state = 'on'
                        time.sleep(config.displayTime)

                    if 'off' in text :
                        #lcd.clear()
                        lcd.home()
                        time.sleep(.1)
                        lcd.message("OFF command")               
                        show('Output is now off')
                        GPIO.output(config.lightsPin, False)
                        state = 'off'                            
                        time.sleep(config.displayTime)             

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
                            lcd.clear()
                            lcd.home()
                            time.sleep(.1)
                            lcd.message("Status request:\n")
                            lcd.message("Pin is " + str(state))
                            show("Status was requested. Pin state is " + state)
                        
                        t = 'Pin state is ' + str(GPIO.input(config.inputPin)) + '\nOutput is ' + str(state)
                        
                        sendEmail(sender, 'Status report', t)
                        time.sleep(config.displayTime)
        

        except Exception, detail :
            print "ERROR: " + str(detail)
            
        GPIO.output(config.backlightPin, False)
        if config.verbose :    
            show("Sleeping for " + str(config.sleepTime) + " seconds", say=False)
        lcd.home()
        lcd.clear()
        time.sleep(.1)
        lcd.message("Sleeping for")
        timer = config.sleepTime
        
        
        while timer > 0 :
            lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
            lcd.message(str(timer) + " seconds")
            timer -= 1
            time.sleep(1)

        
        
    



