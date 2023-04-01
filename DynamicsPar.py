from cosapp.base import System

from Ports import VelPort, AclPort
from Utility.Utility import thrust

import numpy as np

from scipy.spatial.transform import Rotation as R


class DynamicsPar(System):
    def setup(self):

        #System orientation
        self.add_inward('DynPar_ang', np.zeros(3), desc = "Earth Euler Angles", unit = '')
        
        self.add_inward('l0', 1., desc = "Rope rest length", unit = 'm')
        self.add_inward('k', 100., desc = "rope's stiffness", unit='N/m')
        self.add_inward('m1', 1.6, desc = "Mass of parachute + nosecone", unit = 'kg')
        self.add_inward('m2', 10., desc = "Mass of rocket - nosecone", unit = 'kg')
        self.add_inward('S_ref', .1, desc = "Reference surface of parachute", unit = 'm**2')
        self.add_inward('Cd', 1.75, desc = "Drag coefficient of parachute", unit = '')
        self.add_inward('r_in', np.zeros(3), desc = "Rocket Position", unit = 'm')
        self.add_inward('ang', np.zeros(3), desc = "Rocket angular position", unit = 'm')
        self.add_inward('Dep', 0., desc = "Parachute Deployed", unit = '')
        
        self.add_input(AclPort, 'g')
        self.add_input(VelPort, 'v_wind')
        self.add_input(VelPort, 'v_in')

        #Dynamics outputs
        self.add_outward('a1', np.zeros(3), desc = "Parachute + nosecone Acceleration", unit = 'm/s**2')
        self.add_outward('a2', np.zeros(3), desc = "Rocket - nosecone Acceleration", unit = 'm/s**2')

        #Transients
        self.add_transient('v1', der='a1')
        self.add_transient('v2', der='a2')
        self.add_transient('r1', der='v1') #correspond au parachute auquel est attaché le nosecone (extrémité haute de la corde)
        self.add_transient('r2', der='v2') #correspond au haut du tube de la fusée (extrémité basse de la corde)

        #Event
        self.add_event("ParachuteDeployed", trigger='v_in.val[2] < 0')

    def transition(self):

        if self.ParachuteDeployed.present:

            print("R1 ABOUGA")
            print(self.r1)
            self.Dep = 1
            l0 = [self.l0,0,0]
            rotation = R.from_euler('xyz', self.ang, degrees=False)
            vect1 = rotation.apply(l0)
            self.r1 = self.r1 + l0
            print(self.r1, self.r2)
            print("R1 ABOUGA")


        
    def compute(self):

        if self.Dep == 0:
            # print("not deployed yet")
            # print("r_in")
            # print(self.r_in)
            # print("angles")
            # print(self.ang)
            self.v1 = np.zeros(3)
            self.v2 = np.zeros(3)
            self.r1 = np.array([100,0,0])
            self.r2 = np.array([100,0,0])

            # print("r1")
            # print(self.r1)
            # print("r2")
            # print(self.r2)
            # print("v1")
            # print(self.v1)

        else:
            # print("deployed")
            # print("r1")
            # print(self.r1)
            # print("r2")
            # print(self.r2)
            # print("v1")
            # print(self.v1)
            Drag = -.5 * self.S_ref * self.Cd * np.linalg.norm(self.v1) * (self.v1-self.v_wind.val) 
            # print("Drag")
            # print(Drag)
            # print(self.v2)
            d = abs(-self.r2 + self.r1)
            d_norm = 0 if np.linalg.norm(d)<1e-6 else d/np.linalg.norm(d)
            self.a1 = -(self.k / self.m1) * (d-self.l0*d_norm) + np.array([0.,0.,-9.8]) + Drag/self.m1
            self.a2 = -(self.k / self.m2) * (-d+self.l0*d_norm) + np.array([0.,0.,-9.8])