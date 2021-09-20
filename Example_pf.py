# Importamos librerías
import power_flow_library as g
import numpy as np

# Base voltage
Ub = 20e3

# Grid initialization
net = g.grid(Ub)
net.add_bus(ref = 0, slack = True, P = 0, Q = 0, U = Ub) # Slack bus
net.add_bus(ref = 1, slack = False, P = 14e6, Q = 0, U = Ub) # Power injection of 15 MW
net.add_line(Z = 1.63278 + 1.03494j, bus_0 = 0, bus_1 = 1) # Line connecting both buses

# Solving power flow
S0 = net.solve_pf()

# Printing buses voltages in pu
for bus in net.buses:
    print(bus.ref, np.abs(bus.U)/Ub)
    