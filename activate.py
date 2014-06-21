#!/usr/bin/python
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error import RPi.GPIO!  Are you sudo?")

#Set the Pin Numbering Mode: BOARD=the pin number on the board, BCM=the channel numbers
GPIO.setmode(GPIO.BOARD)

#Warnings?
GPIO.setwarnings(False)

def pinSetup(pin,type):
    if type == 'in':
        GPIO.setup(pin, GPIO.IN)
    elif type == 'out':
        GPIO.setup(pin, GPIO.OUT)


if __name__ == '__main__':
    pins = [12]
    for pin in pins:
        pinSetup(pin,'out')

        for pin in pins:
            GPIO.output(pin,1)
            time.sleep(.2)
            GPIO.output(pin,0)
