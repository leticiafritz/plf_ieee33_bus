# ---------- BIBLIOTECAS ----------
import numpy as np
import scipy.stats as ss
import matplotlib.pyplot as plt

# ---------- VARIAVEIS GLOBAIS ----------
# VARIAVEIS GLOBAIS PARA FDP
SD_LOAD = .05
ALFA_PV, BETA_PV = 4, 2.5
MU_EV, SD_EV = 3.2, 0.88 # 30, 5
MU_EV_HOUR_ARRIVE, SD_EV_HOUR = 19, 3.4  # [Wu, 2013], carro estaciona para carregar às 17:36

# VARIAVEIS GLOBAIS PARA PV
R_CERTAIN_POINT = 150
R_STANDARD_CONDITION = 1000
R_FACTOR = 500
PV_POWER_GENERATION = 250
# VARIAVEIS GLOBAIS PARA EV
EV_BATTERY_CAPACITY = 62  # [kWh] Nissan Leaf
EV_CONSUMPTION_KM = 62 / 350  # [kWh] Nissan Leaf
EV_CONSUMPTION_V2G = 0.5
EV_VOLTAGE = 220 # [V]
EV_CURRENT_CHARGE = 32 # [A]

class Sample:
    def __init__(self, load):
        self.load = load

    # FUNÇÃO DE POTÊCIA GERADA DA PV
    def get_pv_sample(self):
        # Função de distribuição de probabilidade da radiação solar
        radiation = ss.beta.pdf(np.linspace(0, 1, 24), ALFA_PV, BETA_PV, 0, 1)  # beta [Yaotang, 2016]
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
    def get_ev_soc(self):
        # Distribuição de probabilidade acumulativa da distância percorrida pelo carro
        dist = np.random.lognormal(MU_EV, SD_EV)

        # Estado da carga da bateria mínimo (o SOC não pode ter menos que 20% de carga no momento da chegada)
        # O SOC não deve ser menor que o SOC_min, durante o período de descarga
        soc_min = 0.2 + ((dist * EV_CONSUMPTION_KM) / (2 * EV_BATTERY_CAPACITY))

        # Energia necessária para carregar totalmente a bateria
        soc_hini = 1 - ((dist * EV_CONSUMPTION_KM + EV_CONSUMPTION_V2G) / EV_BATTERY_CAPACITY)

        # Estado de carga da bateria antes de descarregar
        soc_init = np.random.uniform(soc_hini + soc_min, 1)


        return soc_init, soc_min, soc_hini

    # CONFIGURANDO AMOSTRA
    def get_ev_sample(self):
        # SOC do veículo elétrico
        soc_init, soc_min, soc_hini = self.get_ev_soc()

        # Estimando tempos do carregamento
        t_duration_charge = np.random.randint(2, 6)
        t_start_charge = int(np.random.normal(MU_EV_HOUR_ARRIVE, SD_EV_HOUR))
        while t_start_charge > 24:
            t_start_charge = int(np.random.normal(MU_EV_HOUR_ARRIVE, SD_EV_HOUR))

        # Construindo curva
        curve = [0] * (t_start_charge-1)
        curve.extend([1]*t_duration_charge)
        if len(curve) < 24:
            curve.extend([0]*(24-len(curve)))
        else:
            curve_aux = curve[24:]
            n = len(curve_aux)
            for i in range(n):
                curve[i] = curve_aux[i]
            curve = curve[0:24]

        # Energia do carro
        energy = (soc_init-soc_hini)*EV_BATTERY_CAPACITY
        power = energy / t_duration_charge

        # construindo objeto
        ev = Electricvehicle(soc_init, soc_min, soc_hini, curve, power)

        return ev

    def get_load_sample(self):
        # Carga
        load = np.random.normal(self.load, SD_LOAD)  # distribuição normal [Morshed, 2018]  [Unidade: kWh]

        return load


class Electricvehicle:
    def __init__(self, soc_init, soc_min, soc_hini, curve, power):
        self.soc_init = soc_init
        self.soc_min = soc_min
        self.soc_hini = soc_hini
        self.curve = curve
        self.power = power
