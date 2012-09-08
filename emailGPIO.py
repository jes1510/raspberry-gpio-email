#!/usr/bin/python
'''
Written by Jesse Merritt www.github.com/jes1510 September 8 , 2012

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/

Toggles GPIO pin based on contents of an email
IMAP is used to check the contents of a gMail account.
A GPIO pin is toggled depending on the contents of the body
of the last email received.

Based heavily on example code here:
http://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/
'''

import RPi.GPIO as GPIO
import time
import imaplib
import email
import sys

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.output(11, False)

login = sys.argv[1]
password = sys.argv[2]

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(login, password)
mail.list()
mail.select('inbox')

while True:    
    print 'Checking email...'    
    result, data = mail.uid('search', None, "ALL") 
    latest_email_uid = data[0].split()[-1]
    result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
    raw_email = data[0][1]
   # print raw_email

    def get_first_text_block(email_message_instance):
        maintype = email_message_instance.get_content_maintype()
        if maintype == 'multipart':
            for part in email_message_instance.get_payload():
                if part.get_content_maintype() == 'text':
                    return part.get_payload()

        elif maintype == 'text':
            return email_message_instance.get_payload()


    email_message = email.message_from_string(raw_email)

    print '________________'
    text = get_first_text_block(email_message)
    print text
    if 'on' in text :
        print 'On'
        GPIO.output(11, True)

    if 'off' in text :
        print 'Off'
        GPIO.output(11, False)

    if 'pulse' in text :
        print 'Pulse'
        GPIO.output(11, False)
        time.sleep(1)
        GPIO.output(11, True)
        time.sleep(1)
        GPIO.output(11, False)

    time.sleep(30)




