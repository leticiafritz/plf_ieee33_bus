#################################################################
# NOME: LETÍCIA FRITZ HENRIQUE
# E-MAIL: LETICIA.HENRIQUE@ENGENHARIA.UFJF.BR
# PROJETO: FLUXO DE CARGA PROBABILISTICO COM RED
# VERSÃO: 1.1
# PROXIMO PASSO: 5. ALOCAR LOADSHAPE DA CARGA; 6. ALOCAR LOADSHAPE PV; 7. ALOCAR PONTO DE RECARGA EV
#################################################################

# BIBLIOTECAS
import matplotlib.pyplot as plt
import pandas as pd
from sample import Sample
from grid import DSS
import numpy as np


# FUNÇÃO PRINCIPAL
def main():
    # Carregando arquivos
    load_det = pd.read_csv("curve_load.csv", header=None)

    # Gerando amostras
    sample = Sample(load_det)
    load, pv, ev = sample.get_sample()

    # Construindo a rede
    grid = DSS(r"C:\Users\LeticiaFritz\Documents\01PROJETOSATUAIS\UNICAMP\Seminario\code\ieee34.dss")

    # Resolver o fluxo de potência
    grid.compile_dss()
    grid.solve_dss()

    # Criar LoadShapes
    load_name = grid.get_all_load_names()
    for n in range(len(load_name)):
        grid.set_new_loadshape("LoadShape_" + load_name[n])

    print(load.tolist())
    # Configurar LoadShapes
    grid.dssLoadShapes.First
    for n in range(grid.dssLoadShapes.Count):
        grid.dssText.Command = ""
        grid.dssLoadShapes.Npts = 4
        grid.dssLoadShapes.HrInterval = 1
        grid.dssLoadShapes.Pmult = [0.2, 3, 4, 2]
        grid.dssLoadShapes.Next

# RUN
if __name__ == '__main__':
    main()
