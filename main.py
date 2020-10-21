#################################################################
# NOME: LETÍCIA FRITZ HENRIQUE
# E-MAIL: LETICIA.HENRIQUE@ENGENHARIA.UFJF.BR
# PROJETO: FLUXO DE CARGA PROBABILISTICO COM RED
# VERSÃO: 1.2
# PROXIMO PASSO: 8. UTILIZAR (https://dss-extensions.org/); 9. CALCULAR PDF DAS POTÊNCIAS DE SAÍDA
#################################################################

# BIBLIOTECAS
import matplotlib.pyplot as plt
from sample import Sample
from grid import DSS
from montecarlo import Montecarlo
import numpy as np


# FUNÇÃO PRINCIPAL
def main():

    # Monte Carlo
    simulation = Montecarlo(1)
    simulation.set_simulation()


# RUN
if __name__ == '__main__':
    main()
