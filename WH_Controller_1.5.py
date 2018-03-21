from datetime import datetime
from numpy.random import normal
from numpy import zeros, savetxt, loadtxt
import random
import RPi.GPIO as GPIO
from time import time, sleep
import os


#Initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
FMPIN = 6    #flow meter GPIO pin
VPIN = 17    #valve GPIO pin
GPIO.setup(FMPIN, GPIO.IN, GPIO.PUD_UP) #setup flow meter pin as input
GPIO.setup(VPIN, GPIO.OUT, initial=GPIO.LOW)    #setup valve pin as output
GPIO.add_event_detect(FMPIN, GPIO.RISING)   #add rising edge detection

def generate_schedule():
    events = zeros((24,60))
    hourlySums = zeros(24)

    for hour in range(24):
        if hour < 6 or hour > 22:
            numEvents = int(normal(5,2))
            drawSize = 0.2
            drawSD = 0.05
        elif hour >= 5 and hour < 12:
            numEvents = int(normal(10,5))
            drawSize = 0.75
            drawSD = 0.5
        elif hour >=12 and hour < 17:
            numEvents = int(normal(7,2))
            drawSize = 0.25
            drawSD = 0.1
        elif hour >=17 and hour < 22:
            numEvents = int(normal(15,5))
            drawSize = 0.5
            drawSD = 0.3
        if numEvents > 0:
            minutes = random.sample(range(60),numEvents)
        else:
            numEvents = 0

        for event in range(numEvents):
            eventSize = normal(drawSize,drawSD)
            if eventSize > 0:
                events[hour][minutes[event]] = eventSize

        hourlySums[hour] = sum(events[hour])
    return events,hourlySums

#Define function to draw water
def draw_water(target):
    if target <= 0:
        return()
    print ('Drawing %.2f gallon(s).' % target)
    volume = 0
    numPulses = 0
    start_time = time()
    GPIO.output(VPIN, GPIO.HIGH)    #open valve
    while volume < target:  #keep valve open until desired volume has passed
        if GPIO.event_detected(FMPIN):
            numPulses += 1    #Count pulses from flow meter
            volume = float(numPulses) / 424    #Calculate volume
        run_time = time()
        elapsed_time = run_time - start_time
        if elapsed_time > 50:
            print('Timeout Error.')
            break
    GPIO.output(VPIN, GPIO.LOW) #close valve
    print ('Volume drawn: %.2f gallon(s).' % volume)

#Initialize events array (This will be fixed later)
events = []

#Enter main program loop
while True:
    now = datetime.now()    #Update date/time
    filename = 'WH_Data_' + str(now.month) + '-' + str(now.day) + '-' + str(now.year) + '.csv'
    schedule = 'Schedule' + str(now.month) + '-' + str(now.day) + '-' + str(now.year) + '.csv'
    if not os.path.isfile(filename): #Check if a new day has begun
        data = open(filename, 'w')
        data.write('Hour,Minute,Draw Amount\n')
        data.close
    if os.path.isfile(schedule) and events == []:
        events = loadtxt(schedule,delimiter=',')
    elif not os.path.isfile(schedule):
        events,hourlySums = generate_schedule()
        savetxt(schedule,events,delimiter=',',newline='\n',fmt='%f')
        
    #Draw water if there is an event at this minute
    if events[now.hour][now.minute] != 0 and now.second == 0:
        draw_water(events[now.hour][now.minute])
        data = open(filename, 'a')
        data.write(str(now.hour) + ',' + str(now.minute) + ',' + str(events[now.hour][now.minute])+'\n')
        data.close
    sleep(1)
