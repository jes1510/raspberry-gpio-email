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
'''

import RPi.GPIO as GPIO
import time
import imaplib
import email
import sys
import ConfigParser
import smtplib
import os

config = ConfigParser.SafeConfigParser()
config.read('emailGPIO.cfg')
whiteList = {}
whiteList = config.get('Email', 'WhiteList').split(' ')
sleepTime = config.getint('Email', 'Interval')
outPin = config.getint('Hardware', 'Output')
speak = config.get('Configuration', 'Speak')
verbose = config.get('Configuration', 'Verbose')
approvedSubject = config.get('Email', 'Subject')

sentenceQue = []

state = 'off'

GPIO.setmode(GPIO.BOARD)
GPIO.setup(outPin, GPIO.OUT)
GPIO.output(outPin, False)

login = sys.argv[1]
password = sys.argv[2]

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(login, password)

def show(output, say=True) :
    if verbose :
        print output
        
    if speak and say:
        a = os.system("echo " + output + " | festival --tts")  

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
    if verbose : show('Sending to ' + recipient)
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

while True:
    show('Checking email...', say=False)
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
            if sender in whiteList and subj.upper() == approvedSubject.upper() :      
                show('Command received from ' + name)
                text = get_first_text_block(email_message)       
                    
                if 'on' in text :               
                    show('Output is now on')
                    state = 'on'
                    GPIO.output(outPin, True)

                if 'off' in text :                 
                    show('Output is now off')
                    state = 'off'
                    GPIO.output(outPin, False)               
                                       

                if 'pulse' in text :             
                    show('Pulsing output')
                    GPIO.output(outPin, False)
                    time.sleep(1)
                    GPIO.output(outPin, True)
                    time.sleep(1)
                    GPIO.output(outPin, False)
                    state = 'off'

                if not 'noack' in text or 'status' in text:
                    if 'status' in text :
                        show("Status was requested. Pin state is " + state)
                    t = 'Pin state is ' + str(state)
                    sendEmail(sender, 'Status report', t)                    

    except Exception, detail :
        print "ERROR: " + str(detail)

    if verbose :    
        show("Sleeping for " + str(sleepTime) + " seconds", say=False)
        
    time.sleep(sleepTime)
    



