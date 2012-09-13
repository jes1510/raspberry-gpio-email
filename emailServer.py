'''

based on work here:  http://www.mkyong.com/python/how-do-send-email-in-python-via-smtplib/
'''
import smtplib
import sys
 
to = sys.argv[3]
gmail_user = sys.argv[1]
gmail_pwd = sys.argv[2]
smtpserver = smtplib.SMTP("smtp.gmail.com",587)
smtpserver.ehlo()
smtpserver.starttls()
smtpserver.ehlo
smtpserver.login(gmail_user, gmail_pwd)
header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:testing \n'
print header
msg = header + '\n Test email from ' + gmail_user + '\n\n'
smtpserver.sendmail(gmail_user, to, msg)
print 'done!'
smtpserver.close()
