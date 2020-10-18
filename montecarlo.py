# ---------- BIBLIOTECAS ----------
import pandas as pd
import matplotlib.pyplot as plt
import os
from sample import Sample
from grid import DSS


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

            grid.dssText.Command = "New Monitor.M1_power   element=line.L1   terminal=1   mode=1   ppolar=no"
            grid.solve_dss("daily")
            grid.set_active_bus("860")
            print(grid.get_bus_vmagangle())

            grid.dssText.Command = "Plot Monitor object=M1_power Channels=(1,3,5)"
            grid.get_circuit_result()

