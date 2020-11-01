#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

import sys
sys.path.append('../../../')
from tools.supervision import *

f, I = eval(load("Save.txt"))

figure = matplotlib.pyplot.figure('Graphic', figsize=(14, 8))
matplotlib.pyplot.scatter(I,f,s=1)
matplotlib.pyplot.xlabel('I (A)*winding')
matplotlib.pyplot.ylabel('f (Hz)')
matplotlib.pyplot.xlim(0, 310000)
matplotlib.pyplot.ylim(0, 101)
matplotlib.pyplot.show()
figure.savefig("Graphic.svg", bbox_inches = 'tight', pad_inches=0)
