import numpy as np
from scipy.optimize import fsolve
from scipy.optimize import minimize

class grid:    
    def __init__(self, U):
        self.buses = list() 
        self.lines = list() 
        self.Y = None       
        self.S = list()     
        self.U = U          
    def add_bus(self, ref, slack, P, Q, U = 0):
        self.buses.append(bus(ref, slack, P, Q, U))
    def add_line(self, Z, bus_0, bus_1):
        for bus in self.buses:
            if bus.ref == bus_0:
                BUS_0 = bus
            if bus.ref == bus_1:
                BUS_1 = bus
        self.lines.append(line(Z, BUS_0, BUS_1))
        BUS_0.connections_out.append(self.lines[-1])
        BUS_1.connections_in.append(self.lines[-1])
    def generate_Y(self):
        self.Y = np.zeros((len(self.buses), len(self.buses)), dtype = complex)
        for bus in self.buses:
            for line in bus.connections_in:
                self.Y[bus.ref, line.connections[0].ref] = -1/line.Z
            for line in bus.connections_out:
                self.Y[bus.ref, line.connections[1].ref] = -1/line.Z
        for index in range(self.Y.shape[0]):
            self.Y[index, index] = -np.sum(self.Y[index,:])
        return self.Y
    def generate_S(self):
        self.S = list()
        for bus in self.buses:
            self.S.append(np.complex(bus.P, bus.Q))       
    def solve_pf(self):
        self.generate_S()
        self.generate_Y()
        x_init = list(np.zeros(len(self.buses)*4))
        index = 0
        for bus in self.buses:
            x_init[index] = np.real(self.U)
            index += 1
            x_init[index] = np.imag(self.U)
            index += 1
        sol, infodict, ier, mesg = fsolve(self.constraints, x_init, full_output = True)
        if ier != 1:
            print(mesg)  
        index = 0
        for bus in self.buses:
            bus.set_U(np.complex(sol[index], sol[index + 1]))
            index += 2
        for bus in self.buses:
            bus.set_I(np.complex(sol[index], sol[index + 1]))
            index += 2
        for line in self.lines:
            line.I = (line.connections[0].U/np.sqrt(3) - line.connections[1].U/np.sqrt(3))/line.Z
        return np.sqrt(3)*self.buses[0].U*np.conjugate(self.buses[0].I)
    def constraints(self, x):
        voltages = np.zeros(len(self.buses), dtype = complex)
        currents = np.zeros(len(self.buses), dtype = complex)
        index = 0
        for item in range(0, len(self.buses)*2, 2):
            voltages[index] = np.complex(x[item], x[item + 1])
            index += 1
        index = 0
        for item in range(len(self.buses)*2, len(self.buses)*4, 2):
            currents[index] = np.complex(x[item], x[item + 1])
            index += 1
        cost = list(currents - np.dot(self.Y, voltages/np.sqrt(3)))
        cost += list(np.sqrt(3)*voltages[1:]*np.conjugate(currents[1:]) - self.S[1:])
        c =  []
        for item in cost:
            c.append(np.real(item))
            c.append(np.imag(item))
        c += [x[0] - np.real(self.U), x[1] - np.imag(self.U)]
        return c  
    
   
    
class line:
    def __init__(self, Z, BUS_0, BUS_1):
        self.Z = Z
        self.I = 0
        self.connections = [BUS_0, BUS_1]
    def assign_I(self, I):
        self.I = I

class bus:  
    def __init__(self, ref, slack, P, Q, U):
        self.ref = ref
        self.U = U
        self.slack = slack
        self.P = P
        self.Q = Q
        self.I = 0
        self.connections_in = list()
        self.connections_out = list()
    def set_U(self, U):
        self.U = U
    def set_S(self, P, Q):
        self.P = P
        self.Q = Q
    def set_I(self, I):
        self.I = I