# ---------- BIBLIOTECAS ----------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sample import Sample
from grid import DSS

# ---------- VARIAVEIS GLOBAIS ----------
PV_BUS_LIST = ["810", "818", "820", "822", "838", "840", "842", "844", "846", "848", "856", "862", "864", "890"]
PV_BUS_NODE_LIST = [".2", ".1", ".1", ".1", ".2", ".1.2.3", ".1", ".1.2.3", ".2", ".1.2.3", ".2", ".2", ".1",
                    ".1.2.3"]
PV_BUS_PHASE_LIST = [1, 1, 1, 1, 1, 3, 1, 3, 1, 3, 1, 1, 1, 3]
PV_BUS_KV_LIST = [14.376, 14.376, 14.376, 14.376, 14.376, 24.900, 14.376, 24.900, 14.376, 24.900, 14.376, 14.376,
                  14.376, 24.900]
PV_BUS_KW_LIST = [8.0, 17.0, 17.0, 67.5, 14.0, 27.0, 4.5, 405.0, 12.5, 60.0, 2.0, 14.0, 1.0, 450.0]
PV_BUS_KW_LIST = [element * 0.75 for element in PV_BUS_KW_LIST]
EV_BUS_LIST = ["840", "844", "848", "860", "890"]
EV_BUS_CONNECTION_LIST = ["wye", "wye", "delta", "wye", "delta"]
EV_BUS_MODEL_LIST = [5, 2, 1, 1, 5]
EV_BUS_KV_LIST = [24.900, 24.900, 24.900, 24.900, 4.160]
EV_BUS_MAX_NUMBER_LIST = [3, 41, 6, 6, 45]


def get_daily_load(sample, grid):
    # Criar LoadShapes
    load_name = grid.get_all_load_names()
    for i in range(len(load_name)):
        grid.set_new_loadshape("LoadShape_" + load_name[i])

    # Configurar LoadShapes
    grid.dssLoadShapes.First
    for i in range(grid.dssLoadShapes.Count):
        grid.dssLoadShapes.Npts = 24
        grid.dssLoadShapes.HrInterval = 1
        # Gerando amostras
        load = sample.get_load_sample()
        new_load = [float(item) for item in load]
        grid.dssLoadShapes.Pmult = new_load
        grid.dssLoadShapes.Normalize()
        grid.dssLoadShapes.Next

    # Acrescentar loadshape nas cargas
    grid.dssLoads.First
    for i in range(grid.dssLoads.Count):
        grid.dssLoads.daily = "LoadShape_" + load_name[i]
        grid.dssLoadShapes.Next


def get_daily_pv(sample, grid):
    # Cria loadshape com as curvas de geração PV
    for item in PV_BUS_LIST:
        grid.set_new_loadshape("LoadShape_pv_" + item)
    grid.dssLoadShapes.First
    for i in range(grid.dssLoadShapes.Count):
        if i < grid.dssLoadShapes.Count - len(PV_BUS_LIST):
            grid.dssLoadShapes.Next
        else:
            grid.dssLoadShapes.Npts = 24
            grid.dssLoadShapes.HrInterval = 1
            # Gerando amostras
            pv = sample.get_pv_sample()
            new_pv = [float(item) for item in pv]
            grid.dssLoadShapes.Pmult = new_pv
            grid.dssLoadShapes.Normalize()
            grid.dssLoadShapes.Next

    # Criando geradores PV
    for i in range(len(PV_BUS_LIST)):
        grid.dssText.Command = "New Generator.PV_" + PV_BUS_LIST[i] + " phases=" + str(PV_BUS_PHASE_LIST[i])
        grid.dssText.Command = "~ bus1=" + PV_BUS_LIST[i] + PV_BUS_NODE_LIST[i] + " kv=" + str(PV_BUS_KV_LIST[i])
        grid.dssText.Command = "~ kW=" + str(PV_BUS_KW_LIST[i]) + " pf=1 model=1 conn=wye"
        grid.dssText.Command = "~ daily=LoadShape_pv_" + PV_BUS_LIST[i]


def get_daily_ev(sample, grid):
    # Cria loadshape com carregamento de EV
    for item in EV_BUS_LIST:
        grid.set_new_loadshape("LoadShape_ev_" + item)
    grid.dssLoadShapes.First
    n = 0
    ev_power = [0]*len(EV_BUS_LIST)
    for i in range(grid.dssLoadShapes.Count):
        if i < grid.dssLoadShapes.Count - len(EV_BUS_LIST):
            grid.dssLoadShapes.Next
        else:
            grid.dssLoadShapes.Npts = 24
            grid.dssLoadShapes.HrInterval = 1
            # Gerando amostras
            ev = sample.get_ev_sample()
            ev_power[n] = ev.power
            n = n + 1
            grid.dssLoadShapes.Pmult = ev.curve
            grid.dssLoadShapes.Normalize()
            grid.dssLoadShapes.Next

    # Criando carga PEV
    for i in range(len(EV_BUS_LIST)):
        total_power = np.random.randint(int(EV_BUS_MAX_NUMBER_LIST[i] / 3), EV_BUS_MAX_NUMBER_LIST[i]) * ev_power[i]
        print(total_power)
        grid.dssText.Command = "New Load.EV_" + EV_BUS_LIST[i] + " bus1=" + EV_BUS_LIST[i] + " phases=3"
        grid.dssText.Command = "~ conn=" + EV_BUS_CONNECTION_LIST[i] + " Model=" + str(EV_BUS_MODEL_LIST[i])
        grid.dssText.Command = "~ kV=" + str(EV_BUS_KV_LIST[i]) + " kW=" + str(total_power) + " kVAR=10"
        grid.dssText.Command = "~ Status=variable daily=LoadShape_ev_" + EV_BUS_LIST[i]

class Montecarlo:
    def __init__(self, number):
        self.number = number

    def set_simulation(self):
        # Carregando arquivos
        load_det = pd.read_csv("curve_load.csv", header=None)

        # Gerando amostras
        sample = Sample(load_det)

        # Construindo a rede
        grid = DSS(os.getcwd() + "\ieee34.dss")

        for n in range(self.number):
            # Compilando a rede
            grid.compile_dss()

            # Colocando curva de carga nas barras
            get_daily_load(sample, grid)

            # Colocando curva de geração nas barras
            get_daily_pv(sample, grid)

            # Colocando curva de PEV
            get_daily_ev(sample, grid)

            grid.dssText.Command = "New Monitor.M1_power   element=line.L32   terminal=1   mode=1   ppolar=no"
            grid.dssText.Command = "New Monitor.M1_voltage   element=line.L32   terminal=1   mode=0"
            grid.solve_dss("daily")
            grid.set_active_bus("860")
            print(grid.get_bus_vmagangle())

            grid.dssText.Command = "Plot Monitor object=M1_power Channels=(1,3,5)"
            grid.dssText.Command = "Plot Monitor object=M1_voltage Channels=(1,3,5)"
            grid.get_circuit_result()
