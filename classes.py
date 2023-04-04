# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 14:40:03 2022

@author: thoma
"""

import pygame, sys, os
from pygame.locals import*
import matplotlib as mpl
import matplotlib.pyplot as plt
import csv
import numpy as np

"""
mpl.rcParams['lines.linewidth'] = 2
mpl.rcParams['lines.linestyle'] = '--'
"""
pygame.init()
color_dark = (48,48,48)
color_light = (30,40,230)
color_active = (255,255,255)
color_passive = (240,240,240)
#plt.style.use('plot.mplstyle')
mpl.use('module://pygame_matplotlib.backend_pygame')



class button:
    def __init__(self,texte, loc,fenetre):
        self.texte = texte
        self.box = pygame.draw.rect(fenetre, color_dark, [loc[0], loc[1], 90 , 30])
        self.smallfont = pygame.font.SysFont('Corbel',16, True) 
        self.text = self.smallfont.render(texte[0] , True , (255,255,255))
        fenetre.blit(self.text , (loc[0]+10,loc[1]+7))
        self.loc = loc
        self.active = False
    def refresh(self,wind):
        if self.active:
            self.color = color_light
            self.text = self.smallfont.render(self.texte[1] , True , (255,255,255))
        else:
            self.color = color_dark
            self.text = self.smallfont.render(self.texte[0] , True , (255,255,255))

        pygame.draw.rect(wind, self.color, [self.loc[0], self.loc[1], 90 , 30])
        wind.blit(self.text , (self.loc[0]+10,self.loc[1]+7))

class box:
    def __init__(self,intit,loc, fenetre):
        self.user_text = ''
        self.intit = intit
        # create rectangle
        self.color = color_dark
        self.input_rect = pygame.draw.rect(fenetre, color_passive, [loc[0], loc[1],90, 30])
        self.active = False
        self.smallfont = pygame.font.SysFont('Corbel',16, True) 
        self.inactive_font =pygame.font.SysFont('Corbel',10, True,True)
        self.timer = 0
        self.dif = "0.00"
    def refresh(self,wind):
        if self.active:
            self.color = color_active
            pygame.draw.rect(wind, self.color,self.input_rect)
            text_surface = self.smallfont.render(self.user_text, True, (0, 0, 0))
        else:
            self.color = color_passive    
            pygame.draw.rect(wind, self.color,self.input_rect)
            text_surface = self.smallfont.render(self.user_text, True, (0,0,0))
        wind.blit(text_surface, (self.input_rect.x+5, self.input_rect.y+5))
        if self.user_text == "" and not self.active:
            text_surface = self.inactive_font.render(self.intit, True, (0,0,0))
            wind.blit(text_surface, (self.input_rect.x+5, self.input_rect.y+10))
        # set width of textfield so that text cannot get
        # outside of user's text input
        self.input_rect.w = max(90, text_surface.get_width()+10)
    def affiche(self,wind,val):
        self.timer +=1
        if self.timer >5:
            self.timer = 0
            self.dif = val
        self.color = color_passive
        pygame.draw.rect(wind, self.color,self.input_rect)
        text_surface = self.smallfont.render(self.dif, True, (0, 0, 0))
        wind.blit(text_surface, (self.input_rect.x+5, self.input_rect.y+10))

      
class plotter:
    def __init__(self,loc,nb,sub,res, title):
        self.nb = nb
        self.size = res
        self.sub = sub
        self.title = title
        self.loc = loc
        self.img = pygame.image.load('temp' + str(self.nb)+'.png').convert()
        self.fig, self.axes = plt.subplots(figsize =self.size,facecolor=(78/255, 181/255, 207/255),
                                      edgecolor = "grey")
        plt.figure(self.nb)
        self.axes.grid()
        self.axes.set_title(self.title[0], fontweight='bold')
        self.axes.set_xlim(0,5)
        self.start = 0
        self.memory = 0
        self.xlimt = 5
        self.timer = 0.2
        self.axes.set_xlabel("Time (s)")
        self.axes.set_ylabel("Pressure (mbar)",rotation ="horizontal")

    def menu(self,wind):
        self.fig.canvas.draw()
        wind.blit(self.fig, self.loc)
    def nett(self):
        self.fig.clear()
        self.memory = 0
        self.xlimt = 5
        self.timer = 0.2
        self.fig, self.axes = plt.subplots(figsize =self.size,facecolor=(78/255, 181/255, 207/255),
                                      edgecolor = "grey")
        plt.figure(self.nb)
        self.axes.grid()
        self.axes.set_xlim(0,5)
        self.axes.set_xlabel("Time (s)")
        self.axes.set_ylabel("Pressure (mbar)")
        self.axes.set_title(self.title[0], fontweight='bold')
        self.start = 0
    def nett_2(self,time,ts):
        self.fig.clear()
        self.xlimt = time[ts[-1]]+5
        self.start = ts[-1]
        self.fig, self.axes = plt.subplots(figsize =self.size,facecolor=(78/255, 181/255, 207/255),
                                      edgecolor = "grey")
        plt.figure(self.nb)
        self.axes.grid()
        self.axes.set_xlim(time[self.start],self.xlimt)
        self.axes.set_xlabel("Time (s)")
        self.axes.set_ylabel("Pressure (mbar)")
        self.axes.set_title(self.title[0], fontweight='bold')
        self.memory = 0
    def refresh(self,tab,time,wind,ts):
        if len(time)>0 and self.timer < time[-1]:
            self.timer = 0.2 + time[-1]
            if time[-1]>self.xlimt-0.2:
                self.xlimt = time[-1] + (1/3)*(time[-1]-time[self.start])
            self.axes.set_xlim(time[self.start],self.xlimt)
            if len(ts)>0:
                self.start = ts[-1]

            for i in range(len(tab)):
                tab[i][0] = tab[i][0][self.start:]
            time = time[self.start:]
            lines = [0]*len(tab)

            for i in range(len(tab)):
                lines[i] = self.axes.scatter(time[self.memory:],
                    tab[i][0][self.memory:],color=tab[i][1],marker='d',s=10)
            self.axes.set_title(self.title[0], fontweight='bold')
            self.axes.set_xlabel("Time (s)")
            self.axes.set_ylabel("Pressure (mbar)",rotation ="vertical")
            self.memory = len(time)-1

        self.fig.canvas.draw()
        #plt.savefig("temp"+str(self.nb)+".png")
        #plt.close()
        wind.blit(self.fig, self.loc)
        
class recorder:
    """
    Class recorder : create a file,
    """
    def __init__(self,date,memb):
        self.file = open(memb + str(date.year)[-2:]+str(date.month)+
                         str(date.day)+"_"+str(date.hour)+str(date.minute)+str(date.second) 
                         + ".csv", 'w',newline='')
        self.filewriter = csv.writer(self.file) 
        self.filewriter.writerow(["Time\tMerit\tFluigent\tTimestamps"])
    def refresh(self,tab,tabf,time,timestamps):
        for i in range(len(timestamps)):
            self.filewriter.writerow([str(time[i])+"\t"+str(tab[i])+
                                      "\t"+str(tabf[i])+"\t"+str(timestamps[i])])
        for i in range(len(timestamps),len(tab)):
            self.filewriter.writerow([str(time[i])+"\t"+str(tab[i])+
                                      "\t"+str(tabf[i])])
    def end(self):
        self.file.close()

class timer:
    """class timer : crée un timer, décide de la fréquence, à chaque période
    passe à True pour un tick
    """
    def __init__(self,dt):
        self.start = 0
        self.next = dt
        self.active = True
    def update(self,time):
        if self.start+self.next>time:
            self.active= False
        if self.start+self.next <= time:
            self.start = time
            self.active= True
            
            
#Const
pmin = -0.15
pmax = 0.15
MAX = 2**14

def transfer(data):
    data[0],data[1] = '{0:08b}'.format(data[0]),'{0:08b}'.format(data[1])
    data = int((str(data[0])+data[1]),2)
    return (((pmax-pmin)*((data-0.1*MAX)/(0.8*MAX)))+pmin)*68.94757

def add(box,event):
    if event.key == pygame.K_BACKSPACE:
        # get text input from 0 to -1 i.e. end.
        box.user_text = box.user_text[:-1]
    Done = False
    try :
        int(event.unicode)
    except :
        None
    else:
        box.user_text += event.unicode
        Done = True
    if not Done and  str(event.unicode) == ".":
        box.user_text += event.unicode

class carac():
    
    def __init__(self, counter):
        self.stamp = 0
        self.timer = 0
        self.counter = counter
        self.fireis = 0
        self.diff = 0
        self.diff_list=[]
    def actu(self,me,fl,ts,wait):
        fl = np.array(fl)
        me = np.array(me)
        if self.stamp>0:
            if self.counter[self.stamp]==0:
                inp = self.counter[self.stamp-1]
            else:
                inp = self.counter[self.stamp]
        else:
            inp =2
        if len(me)>10:
            self.diff = abs((me[-1]-me[-10]))/(inp*10)
        if not wait:
            if self.diff<0.00007:
                self.timer+=1
            if self.timer>50:
                self.timer = 0
                self.stamp+=1
                self.fireis = 1
        if self.stamp == len(self.counter):
            return -1
        return self.counter[self.stamp]
    def fire(self):
        self.stamp+=1
        self.fireis =1
        self.timer = 0
        return None
    

        """
        if len(tab)<200:
            None
        elif len(tab) == 200:
            self.av = avg(tab)
        elif abs((self.av-avg(tab))/self.av) < 0.005: 
            self.timer += 1
        else :
            self.av = avg(tab)
            self.timer = 0
        if self.timer > 200:
            self.timer = -200
            self.stamp += 1
        if self.stamp == len(self.counter):
            return -1

        return self.counter[self.stamp]

def avg(t):
    s = 0
    for i in range(-200,0):
        s += t[i]
    return s/200
"""

"""
    #fluigent
"""