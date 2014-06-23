This is my shot at making an Alarm that runs off a raspberryPi.

To start that's all it is.  Motion, door, email, client, server.

Why:

I have always wanted to setup my own alarm to fit my needs not what an alarm company provides.  I also don't want to pay a fee to have it monitored when all they do is call me, and the police, who in my area wont respond if it isn't verified, but will still charge me a fee.

I also want other fetures like: light control, smoke/carbon monitoring, HVAC control/monitoring, etc.  I want it in one easy to get place and so far haven't found it.  The trick with this many things and a pi is there aren't enough pins.  You could do wireless, but I dislike batteries.  So I set out to make it scalable to multipul pi's.  Also this way if your pi dies you only loose some lights, not all.

How:

There are right now 5 python files:

activate.py - All this does is turn a pin on wait .2 seconds and turns it back off.  I use this for testing when not at the system itself to pull the door sensor open.

alarmFunctions.py - This is to operate the monitoring of pins and "client" side actions.

commonFunc.py - This is for functions used across the board such and generating an email, and reading yaml files.

master.py - This is the flask web app.  This tells the "client" what pins to monitor, tracks armed zones and system status. If a zone is armed this will fire off the notification email of the action.

piCheck.py - This can be setup on the "server" to run in cron to check if the "Client(s)" have been checking in regularly, of not fire off an email.


Additional files:

There are three addition yaml files needed to run the app:

settings.yaml, pins.yaml, status.yaml.

Settings:  This file defines things need to run the app, where to server is *master*, how often to re-check the configuration/when should we have heard last from the pi, and email settings
```yaml
---
master: '127.0.0.1:5000'
checkinTime: 300
email: {from: 'raspberrypi@domain.com', account: 'user@domain.com', pass: 'pass123', server: 'smtp.domain.com', subject: 'Message From Alarm', to: 'heyyou@domain.com'}
```
pins:  This files sets up the pins, starting with the serial number of the pi the pins are connected to, followed my the pin number and additional info about the pin.  The Pin number does need to match the pin numbering method in the python code.

---
pins:
  0000000000000000:
    15:
      name: 'Front Door' 
      zones:
        - all
        - doors
    11:
      name: 'living room motion'
      zones:
        - all
    13:
      name: 'Back Door'
      zones:
        - all
        - doors

Status: This file will pretty well handle itself.  It mainly exists so if somethings causes a reboot of the app (flask debug mode) it will maintain the status.

armed: []
checkIn: {00000000561867f6: 1403481094.475717}
pins:
  00000000561867f6: {11: 0, 13: 0}



Project Status/resources:

To see where the project is, what features it has, what is in progress/next up go here (https://app.smartsheet.com/b/publish?EQBCT=f59be841a7e646c5a504a180e6625dd1).

Feel free to use and contribute.  If you want to make code style recomendation please contact me directly, I am always looking to learn.
