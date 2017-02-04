
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

import unittest

from MaischStage import *

class TestStringMethods(unittest.TestCase):

    def test_NOT_goToNextWarm(self):
        boil = Maischstatewarm(10, 35)
        self.assertEqual(boil.gotonextorstay(15, 25), False)

    def test_goToNextWarm(self):
        boil = Maischstatewarm(10, 35)
        self.assertEqual(boil.gotonextorstay(15, 35), True)

    def test_NOT_goToNextRest(self):
        boil = Maischstaterest(20, 35)
        self.assertEqual(boil.gottonextorstay(15, 25), False)

    def test_goToNextRest(self):
        boil = Maischstaterest(20, 35)
        self.assertEqual(boil.gottonextorstay(21, 35), True)


    def test_doRun(self):

        steps = [Maischstatewarm(10, 35), Maischstaterest(20, 35), Maischstatewarm(40, 75), Maischstaterest(40, 75), Maischstategotoboil(75, 10, 2040)]

        maischcontroller = Maischcontroller(5, Pump(), Heater(), Thermometer(), Thermometer())
        maischcontroller.doameshrun()


if __name__ == '__main__':
    unittest.main()