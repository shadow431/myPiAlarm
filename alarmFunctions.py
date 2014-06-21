#!/usr/bin/python
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error import RPi.GPIO!  Are you sudo?")

#Set the Pin Numbering Mode: BOARD=the pin number on the board, BCM=the channel numbers
GPIO.setmode(GPIO.BOARD)

#Warnings?
#GPIO.setwarnings(True)

def pinSetup(pin,type):
    if type == 'in':
        GPIO.setup(pin, GPIO.IN)
    elif type == 'out':
        GPIO.setup(pin, GPIO.OUT)

def checkPin(pin):
    return GPIO.input(pin)

if __name__ == '__main__':
    pin = 15
    pinSetup(pin,'in')
    print checkPin(15)
