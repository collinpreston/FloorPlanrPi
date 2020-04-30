#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


distance_list = [] * 360

fig, roomPolarPlot = plt.subplots()
pp = roomPolarPlot.plot([],[])
    

def updatePlot(self, i):
    r = np.arange(1, 361, 1)
    theta = np.radians(r)
    result, = self.pp.plot(theta, self.distance_list)
    
    
def plotDistanceList(self, distance_list):
    self.distance_list = distance_list
    ani = animation.FuncAnimation(self.fig, self.updatePlot, interval=1000)
    plt.show();
        
        
        