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

Use it at your own risk.  Assume that I have no idea what I am doing.

This program establishes a connection to the gMail IMAP server and then  
downloads the latest message.  It will open or close the garage door
by toggling the 'output' pin.  If the door is to be opened or closed
then a warning is shown using a rotating light.  Messages are
shown to the user by a 2 line LCD.  Data is logged to /var/log/messages.


Acceptable commands

'open':  Toggles the 'ouput' pin low to open door.  Checks to make sure it opened.
'close':  Toggles the 'output' pin low to close door.  Checks to make sure it closed.
'status': read status of input pin to check door state.
'ip': Sends the LOCAL ip address 

The system is configured through a configuration file included in the package.
The the pinout is configurable through the configuration file as well.  This
file controls various other things such as verbosity.

The commands must originate from an address listed in the whitelist of the 
configuration file.  This can include a phone number so that control can
be done via a text message. A google voice number is required for receiving text 
messages.  Make sure that the "forward texts to email" option is checked in the 
settings of Google Voice.

The program should be launched with the login credentials and password
as arguments.  A shell script for launching the program as a daemon 
is also included.

GPIO pinout can be found here:
http://elinux.org/images/2/2a/GPIOs.png
