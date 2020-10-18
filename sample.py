# ---------- BIBLIOTECAS ----------
import numpy as np
import scipy.stats as ss

# ---------- VARIAVEIS GLOBAIS ----------
# VARIAVEIS GLOBAIS PARA FDP
SD_LOAD = .05
ALFA_PV, BETA_PV = 4, 2.5
MU_EV, SD_EV = 3.2, 0.88
# VARIAVEIS GLOBAIS PARA PV
R_CERTAIN_POINT = 150
R_STANDARD_CONDITION = 1000
R_FACTOR = 500
PV_POWER_GENERATION = 250
# VARIAVEIS GLOBAIS PARA EV
EV_BATTERY_CAPACITY = 62  # [kWh] [Morshed, 2018]
EV_CONSUMPTION_KM = 0.20  # [kWh] [Wu, 2013]
EV_CONSUMPTION_V2G = 0.10


class Sample:
    def __init__(self, load):
        self.load = load

    # FUNÇÃO DE POTÊCIA GERADA DA PV
    @staticmethod
    def get_pv_sample():
        # Função de distribuição de probabilidade da radiação solar
        radiation = ss.beta.pdf(np.linspace(1, 1, 24), ALFA_PV, BETA_PV, 0, 1)  # beta [Yaotang, 2016]
        radiation = radiation * R_FACTOR

        # Configurando a curva da potência gerada kW
        pv = [0] * 24
        for n in range(np.size(pv)):
            if 0 <= radiation[n] < R_CERTAIN_POINT:
                pv[n] = PV_POWER_GENERATION * (radiation[n] ** 2 / (R_CERTAIN_POINT * R_STANDARD_CONDITION))
            elif R_CERTAIN_POINT <= radiation[n] < R_STANDARD_CONDITION:
                pv[n] = PV_POWER_GENERATION * (radiation[n] / R_STANDARD_CONDITION)
            elif radiation[n] >= R_STANDARD_CONDITION:
                pv[n] = PV_POWER_GENERATION

        return pv

    # FUNÇÃO DE ESTADO DA CARGA DO EV
    @staticmethod
    def get_ev_curve():
        # Distribuição de probabilidade acumulativa da distância percorrida pelo carro
        x = np.linspace(1, 24, 100)
        dist = ss.lognorm.cdf(x, SD_EV, scale=MU_EV)

        # Estado de carga da bateria antes de descarregar
        soc_init = 1 - ((dist * EV_CONSUMPTION_KM) / (2 * EV_BATTERY_CAPACITY))

        # Estado da carga da bateria mínimo (o SOC não pode ter menos que 20% de carga no momento da chegada)
        # O SOC não deve ser menor que o SOC_min, durante o período de descarga
        soc_min = 0.2 + ((dist * EV_CONSUMPTION_KM) / (2 * EV_BATTERY_CAPACITY))

        # Energia necessária para carregar totalmente a bateria
        soc_hini = EV_CONSUMPTION_KM * (1 - (dist * EV_CONSUMPTION_KM + EV_CONSUMPTION_V2G))

        return soc_init, soc_min, soc_hini

    # CONFIGURANDO AMOSTRA
    def get_ev_sample(self):
        # Veículo elétrico
        soc_init, soc_min, soc_hini = self.get_ev_curve()
        ev = Electricvehicle(soc_init, soc_min, soc_hini)

        return ev

    def get_load_sample(self):
        # Carga
        load = np.random.normal(self.load, SD_LOAD)  # distribuição normal [Morshed, 2018]  [Unidade: kWh]
        return load


class Electricvehicle:
    def __init__(self, soc_init, soc_min, soc_hini):
        self.soc_init = soc_init
        self.soc_min = soc_min
        self.soc_hini = soc_hini
