raspberry-gpio-email
====================

Written by Jesse Merritt www.github.com/jes1510 September 8, 2012

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/

This program establishes a connection to the gMail IMAP server and then  
tt downloads the latest message and toggles the GPIO pin accordingly.

Acceptable commands:
'on':  Toggle GPIO pin HIGH
'off':  Toggle GPIO pin LOW
'status': read status of input pin 

The system is configured through a configuration file included in the package.
The the pinout is configurable through the configuration file as well.  This
file controls various other things such as verbosity.

The commands must originate from an address listed in the whitelist of the 
configuration file.  This can include a phone number so that control can
be done via a text message. A google voice number is required for receiving text 
messages.  Make sure that the "forward texts to email" option is checked in the 
settings of Google Voice.

The program should be launched with the login credentials and password
as arguments.  The command can be put into a shell script with permissions
set so no one else can read it for security.