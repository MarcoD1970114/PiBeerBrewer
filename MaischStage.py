"""
Copyright 2017, Marco Dumont

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to
whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of
the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

"""
from threading import Thread

import winsound

from Heater import Heater
from Pump import Pump

from time import *

from Thermometer import Thermometer


class Maischstate:
    starttime = 0

    def start(self, time):
        self.starttime = time

    # delta time for this state and currentMaishTemperature
    def gottonextorstay(self, time, currenttemperature):
        return True

    def beep(self):
        winsound.Beep(2500, 1000)

    def doyourthing(self, heater, time, currenttemperature, currenttempbefore):
        return


class Maischstatewarm(Maischstate):
    # warm time in minutes
    warmtime = -1
    # the temperature to reach
    endtemperature = 0

    def __init__(self, warmtime, endtemperature):
        self.warmtime = warmtime
        self.endtemperature = endtemperature

    def __init__(self, currenttemperature, endtemperature, liters, watt):
        self.warmtime = self.getestimatedwarmingduration(currenttemperature, liters, watt)
        self.endtemperature = endtemperature

    def getcurrentgoaltemperature(self, currenttemperature, deltatimepassed):
        return ((self.endtemperature - currenttemperature) / self.warmtime) * deltatimepassed + currenttemperature

    # gets the estimated time in minutes
    def getestimatedwarmingduration(self, currenttemperature, liters, watt):
        return round(((self.endtemperature - currenttemperature) * 1000 * liters * 4.1868) / (3600 * watt) * 60 * 1.05,
                     0)

    def gotonextorstay(self, time, currenttemperature):
        return currenttemperature >= self.endtemperature

    def doyourthing(self, heater, time, currenttemperature, currenttempbefore):
        goaltemperature = self.getcurrentgoaltemperature(time - self.starttime) - currenttemperature
        if (currenttemperature < self.getcurrentgoaltemperature(time - self.starttime)):
            heater.on(goaltemperature / goaltemperature)
        else:
            heater.off()
        return


class Maischstaterest(Maischstate):
    # duration of rest
    resttime = 0
    # temperature of rest
    resttemperature = 0

    def __init__(self, resttime, resttemperature):
        self.resttime = resttime
        self.resttemperature = resttemperature

    def getresttemperature(self):
        return self.resttemperature

    def gottonextorstay(self, time, currenttemperature):
        return self.resttime < time

    def beep(self):
        return

    def doyourthing(self, heater, time, currenttemperature, currenttempbefore):
        if (currenttemperature < self.resttemperature):
            heater.on((currenttemperature - currenttempbefore) / self.resttemperature)
        else:
            heater.off()
        return


class Maischstateboil(Maischstaterest):
    # boil time is seconds
    def __init__(self, boiltime, hops):
        self.resttemperature = 95
        self.resttime = boiltime

    # time in seconds
    def gottonextorstay(self, time, currenttemperature):
        return self.resttime > time


class Maischhopmoment(Maischstateboil):
    def __init__(self, minutesbeforeend):
        self.resttime = minutesbeforeend
        self.resttemperature = 95

    def getminutesafterstart(self):
        return self.restTime


class Maischstategotoboil(Maischstatewarm):
    def __init__(self, currenttemperature, liters, watt):
        self.warmtime = self.getestimatedwarmingduration(currenttemperature, liters, watt)
        self.endtemperature = 95


# stage controller
# responsible for running the maishing process
class Maischcontroller:
    starttime = time()
    stepsdonetime = []
    steps = []
    pump = None
    heater = None
    thermometerAfter = None
    thermometerBefore = None
    thread = None

    def __init__(self, steps, pump, heater, thermometerAfter, thermometerBefore):
        self.steps = steps
        self.pump = pump
        self.heater = heater
        self.thermometerAfter = thermometerAfter
        self.thermometerBefore = thermometerBefore

    def doameshrun(self):
        pointer = 0
        self.pump.on()
        while len(self.steps) > pointer:
            step = self.steps[pointer]
            duration = (time() - self.starttime) - sum(self.stepsdonetime)

            if step.gottonextorstay(duration, self.thermometerAfter.gettemp()):
                pointer += 1
                step.beep()
                self.stepsdonetime.append(duration)
                self.steps[pointer].start(sum(self.stepsdonetime))

            step.doyourthing(heater=self.heater, currenttemperature=self.thermometerAfter.gettemp(),
                             currenttempbefore=self.thermometerBefore.gettemp())

            sleep(1)
        self.heater.off()
        self.pump.off()

    def start(self):
        self.starttime = time()
        self.thread = Thread(target=self.doameshrun)
        self.thread.start()
