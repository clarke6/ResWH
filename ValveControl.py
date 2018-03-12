import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

PIN = 12
GPIO.setup(PIN, GPIO.OUT, initial=GPIO.LOW)

while True:
    x = raw_input('1 to open, 2 to close: ')
    if x == '1':
        GPIO.output(PIN, GPIO.HIGH)
        print '\n Valve Open \n'
    elif x == '2':
        GPIO.output(PIN, GPIO.LOW)
        print '\n Valve Closed \n'
