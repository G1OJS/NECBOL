
import numpy as np
import matplotlib.pyplot as plt
import math


Xpos=np.array([0,0,0,0,0])
Ypos=np.array([-1,-0.5,0,0.5,1])
Zpos=np.array([6,7,8,7,6])
Amp=np.array([1,1,1,1,1])
Phs=np.array([-3.14,-3.14/2,0,3.14/2,3.14])
Lam=300/144.3


def efield(th,phi):
  cth=math.cos(th)
  sth=math.sin(th)
  cph=math.cos(phi)
  sph=math.sin(phi)
  dot=Xpos*sth*cph+Ypos*sth*sph+Zpos*cth
  e=Amp*np.exp(1j*(dot*2*math.pi/Lam+Phs))
  return(sum(e))

def phi_cut():
  e=[]
  for p in phi:
    e.append(20*np.log10(abs(efield(th,p))))
  return(e)

gra=0.95
grp=math.pi
Xpos=np.concatenate([Xpos,Xpos])
Ypos=np.concatenate([Ypos,Ypos])
Zpos=np.concatenate([Zpos,-Zpos])
Amp=np.concatenate([Amp,gra*Amp])
Phs=np.concatenate([Phs,Phs+grp])
 
th=85*math.pi/180
phi=np.linspace(-math.pi,math.pi,359)
plt.plot(phi, phi_cut())
plt.grid(True)
plt.show()
