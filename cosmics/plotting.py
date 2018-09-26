#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

def mark_plot(fx, fy, s):
    ydn,yup = plt.ylim()
    xdn,xup = plt.xlim()
    posx = xdn + (xup-xdn) * fx
    posy = ydn + (yup-ydn) * fy
    plt.text(posx, posy, s,size=14)
