# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 13:31:11 2022

@author: thoma
"""

import pygame, sys, os
from pygame.locals import*
from classes import*
import csv
from datetime import datetime as dt
from Fluigent.SDK import*
from PyMCP2221A import PyMCP2221A
import math
import ctypes
import threading
from pymeasure.instruments.agilent import Agilent34410A

pygame.init()
memb = "coll_9C_"
bon = "images/vessel.png"
myappid = bon # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)



#Initiation
"""
ID=(0x04D8,0xEC79)
inst = PyMCP2221A.PyMCP2221A(VID = ID[0], PID = ID[1])
"""
#multi = Agilent34410A('USB0::0x0957::0x0607::MY47019490::INSTR')
fgt_init()
ch = 0
bg = (78, 181, 207)
clock = pygame.time.Clock()
QC = 0
#résolution
res = (pygame.display.Info().current_w-75,pygame.display.Info().current_h-50)
#res = (pygame.display.Info().current_w,pygame.display.Info().current_h)
fenetre = pygame.display.set_mode(res)
icone = pygame.image.load(bon).convert_alpha()


def terminate():
    pygame.quit()
    sys.exit()
    

pygame.display.set_icon(icone)
pygame.display.set_caption("Title", bon)
pygame.display.set_caption("TYQTOK GUI Fluigent/Merit Sensor Periodic Pressure")
continuer=True

widgets = []
#initialisation des boutons
st = button(["START","STOP"],(100,50),fenetre)
rc = button(["RECORD","STOP REC"], (100,90),fenetre)
det = button(["SET","SET"], (200,90),fenetre)
nett = button(["CLEAR","CLEAR"], (100,130),fenetre)
sinu = button(["SET SIN","SET SIN"],(700,90),fenetre)
auto = button(["AUTO","STOP AUTO"],(700,130),fenetre)
fire = button(["FIRE","FIRE"],(700,170),fenetre)
ref = button(["REF","REF ACTIVE"],(900,50),fenetre)
#Inititalisation des paramètres
press = box("PRESSION (mbar)",(200,50),fenetre)
f = box("FREQUENCE (Hz)",(600,50),fenetre)
offset = box("OFFSET (mbar)",(600, 90),fenetre)
amp = box("AMPLITUDE (mbar)",(700,50),fenetre)
dif_ = box("Diff (Norm)",(600,170),fenetre)
val_ref_box = box("Val Ref (mbar)",(900,90),fenetre)
widgets.append(st)
widgets.append(rc)
widgets.append(det)
widgets.append(nett)
widgets.append(sinu)
widgets.append(press)
widgets.append(f)
widgets.append(offset)
widgets.append(amp)
widgets.append(auto)
widgets.append(fire)
widgets.append(ref)
#Initialisation des plotters
fluig = plotter((25,res[1]-450), 1,111, (8,6),["Input (cyan) and Output (magenta)"])
merit= plotter((600,res[1]-450), 2,111  , (8,6),["Output (magenta)"])
ref_timer =0
#timers :
t_fl = timer(300)
t_pl = timer(1500)
time,tab,tabf,timestamps = [],[],[],[]
record = False
nett.active = False
inp = [0,1,0]
val_fl = 0
diff_val = 0.0
val_ref = 0
# Loop -----------------------------------------------------------------------#
while continuer:
    if not st.active:
        fenetre.fill(bg)
        start = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not st.active and st.box.collidepoint(event.pos):
                    st.active = True
                if not rc.active and nett.box.collidepoint(event.pos):
                    nett.active = True
                    tab = []
                    time = []
                    tabf = []
                    timestamps = []
                    fluig.refresh([[tabf,"c"],[tab,'m']],time,fenetre,timestamps)
                    merit.refresh([[tab,"c"]],time,fenetre,timestamps)

        for w in widgets:
            w.refresh(fenetre)
        dif_.affiche(fenetre,str(diff_val)[0:min(len(str(diff_val)),9)])
        val_ref_box.affiche(fenetre,str(val_ref)[0:min(len(str(val_ref)),9)])
        fluig.menu(fenetre)
        merit.menu(fenetre)
        
        pygame.display.flip()
        clock.tick(30)
        continue
    fenetre.fill(bg)
    for event in pygame.event.get():
        det.active = False
        sinu.active = False
        nett.active = False
        fire.active = False
        if event.type == QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                terminate()
            if press.active :        
                add(press,event)
            if offset.active:
                add(offset,event)
            if f.active:
                add(f,event)
            if amp.active:
                add(amp,event)
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if press.input_rect.collidepoint(event.pos):
                press.active = True
            else:
                press.active = False
            if f.input_rect.collidepoint(event.pos):
                f.active = True
            else:
                f.active = False
            if amp.input_rect.collidepoint(event.pos):
                amp.active = True
            else:
                amp.active = False
            if offset.input_rect.collidepoint(event.pos):
                offset.active = True
            else:
                offset.active = False

            if not auto.active and auto.box.collidepoint(event.pos):
                auto.active = True
                counter = [0,2,0,2,0,2,0,4,0,8,0]
                car = carac(counter)
                wait = False
                wait_c = 0
            elif auto.active and auto.box.collidepoint(event.pos):
                auto.active = False

            if not st.active and st.box.collidepoint(event.pos):
                st.active = True
            elif st.active and st.box.collidepoint(event.pos):
                st.active = False
            if not rc.active and rc.box.collidepoint(event.pos):
                rc.active = True
                tab = []
                time = []
                tabf = []
                timestamps = []
                fluig.nett()
                merit.nett()
                start = pygame.time.get_ticks()
                file = recorder(dt.now(), memb)
            elif rc.active and rc.box.collidepoint(event.pos):
                rc.active = False
                file.refresh(tab,tabf,time,timestamps)
                file.end()
            if det.box.collidepoint(event.pos):
                det.active = True
                if press.user_text == "":
                    inp = [0,0,0]
                else:
                    inp = [0,0,float(press.user_text)]
            if not rc.active and nett.box.collidepoint(event.pos):
                nett.active = True
                tab = []
                time = []
                tabf = []
                timestamps = []
                fluig.nett()
                merit.nett()          
                start = pygame.time.get_ticks()
            if auto.active and fire.box.collidepoint(event.pos):
                car.fire()
                fire.active = True
            if sinu.box.collidepoint(event.pos):
                sinu.active = True
                if amp.user_text=='' or f.user_text == '' or offset.user_text == '':
                    inp = [0,0,0]
                else:
                    inp = [float(amp.user_text),float(f.user_text),float(offset.user_text)]
            if ref.box.collidepoint(event.pos):
                ref.active = True
            if ref.box.collidepoint(event.pos) and ref.active:
                ref.active = False

                
     #lecture et écriture
    time.append((pygame.time.get_ticks()-start)/1000)
    #merit
    """
    data = transfer(inst.I2C_Read(0x28,2))
    tab.append(data)
    """
    p = multi.voltage_dc * 2.6008 - 1.3407
    tab.append(p)
    if auto.active:
        diff_val = car.diff
        if car.fireis:
            wait = True
            wait_c = 3000
        if wait_c != 0:
            wait_c-=1
        if wait_c == 0:
            wait = False
        x = car.actu(tab,tabf,timestamps,wait)
        if x ==-1 :
            auto.active = False
        else:
            inp = [0,0,x]
    if ref.active:
        if ref_timer >0:
            ref_timer -= 1
        if p>10 and ref_timer==0:
            ref_timer = 100
            val_ref +=10
            fgt_set_pressure(2,val_ref)

    fl = inp[0]*math.sin(time[-1]*inp[1])+ inp[2]
    if det.active or (auto.active and car.fireis):
        timestamps.append(len(time)-1)
        fluig.nett_2(time,timestamps)
        merit.nett_2(time,timestamps)
        fgt_set_pressure(ch,fl)
        t_pl.start = pygame.time.get_ticks()
        if auto.active:
            car.fireis = 0
    val_fl = fgt_get_pressure(ch)
    tabf.append(val_fl)
    t_pl.update(pygame.time.get_ticks())
    t_fl.update(pygame.time.get_ticks())

    #Buttons and boxes 
    for w in widgets :
        w.refresh(fenetre)
    dif_.affiche(fenetre,str(diff_val)[0:min(len(str(diff_val)),9)])
    val_ref = fgt_get_pressure(2)
    val_ref_box.affiche(fenetre,str(val_ref)[0:min(len(str(val_ref)),9)])

    #plotters
    fluig.refresh([[tabf,"c"],[tab,'m']],time,fenetre,timestamps)
    merit.refresh([[tab,"m"]],time,fenetre,timestamps)
        
        
    pygame.display.flip()
    clock.tick(10)
pygame.quit()
fgt_set_pressure(ch,0)
file.end()
fgt_set_pressure(ch,0)
fgt_close()
merit.close()
fluig.close()
