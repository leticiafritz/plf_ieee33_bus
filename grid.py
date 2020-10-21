# ---------- BIBLIOTECAS ----------
import win32com.client
#import dss


class DSS:
    def __init__(self, path_dss):
        self.path_dss = path_dss

        # Criar a conexão entre Python e OpenDSS
        self.dssObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
        #self.dssObj = dss.DSS

        # Iniciar o Objeto DSS
        if not self.dssObj.Start(0):
            print("Ops! Problemas em iniciar o OpenDSS")
        else:
            # Criar variáveis para as principais interfaces
            self.dssText = self.dssObj.Text
            self.dssCircuit = self.dssObj.ActiveCircuit
            self.dssSolution = self.dssCircuit.Solution
            self.dssCktElement = self.dssCircuit.ActiveCktElement
            self.dssBus = self.dssCircuit.ActiveBus
            self.dssLines = self.dssCircuit.Lines
            self.dssLoads = self.dssCircuit.Loads
            self.dssLoadShapes = self.dssCircuit.LoadShapes
            self.dssTransformers = self.dssCircuit.Transformers
            self.dssGenerators = self.dssCircuit.Generators

    # Função que retorna a versão
    def versao_dss(self):
        return self.dssObj.Version

    # Função de compila o circuito direcionado pela classe
    def compile_dss(self):
        # Limpar informações das simulações anteriores
        self.dssObj.ClearAll()

        # Compilando arquivo com informações da rede
        self.dssText.Command = "compile " + self.path_dss

        # Acrescentando o Energymeter
        self.dssText.Command = "New Energymeter.M1  Line.L1  1"

    # Função que roda o fluxo de potência
    def solve_dss(self, mode):
        # Configurações da solução
        if mode == "snapshot":
            self.dssText.Command = "Set Mode=snapshot"
            self.dssText.Command = "Set ControlMode=Static"
        elif mode == "daily":
            self.dssText.Command = "Set Mode=daily"
            self.dssText.Command = "Set stepsize=1h"
            self.dssText.Command = "Set number=24"
        self.dssSolution.Solve()

    # ---------- GET CIRCUIT ----------
    # Função que retorna as potências
    def get_circuit_result(self):
        self.dssText.Command = "Show powers kva elements"

    # Função que retorna o nome do circuito
    def get_circuit_name(self):
        return self.dssCircuit.Name

    # Função que retorna as potências ativa e reativa totais do circuito
    def get_circuit_power(self):
        # Negativo para pegar a potência ativa entrando na barra
        p = - self.dssCircuit.TotalPower[0]
        q = - self.dssCircuit.TotalPower[1]
        return p, q

    # ---------- GET CIRCUIT BUS ----------
    # Função que retorna a distancia da barra até o medidor
    def get_bus_distance(self):
        return self.dssBus.Distance

    # Função que retorna o kV base da barra ativa
    def get_bus_kvbase(self):
        return self.dssBus.kVBase

    # Função que retorna magnitude e ângulo da tensão da barra ativa
    def get_bus_vmagangle(self):
        return self.dssBus.VMagAngle

    # ---------- GET CIRCUIT ELEMENT----------
    # Função que retorna as barras de um elemento
    def get_element_bus(self):
        bus = self.dssCktElement.BusNames
        bus1, bus2 = bus[0], bus[1]
        return bus1, bus2

    # Função que retorna as tensões de um elemento
    def get_element_voltage(self):
        return self.dssCktElement.VoltagesMagAng

    # Função que retorna as potências de um elemento
    def get_element_power(self):
        return self.dssCktElement.Powers

    # ---------- GET CIRCUIT LINES ----------
    # Função que retorna o tamanho da linha
    def get_line_name(self):
        return self.dssLines.Name

    # Função que retorna o tamanho da linha
    def get_line_length(self):
        return self.dssLines.Length

    # Função que retorna a lista de linhas do circuito
    def get_all_line_names(self):
        return self.dssLines.AllNames

    # Função que varre todas as linhas e retorna o nome e o tamanho
    def get_all_lines_name_and_length(self):
        # Definindo duas listas
        line_name_list = []
        line_length_list = []

        # Seleciona a primeira linha
        self.dssLines.First
        for n in range(self.dssLines.Count):
            line_name_list.append(self.dssLines.Name)
            line_length_list.append(self.dssLines.Length)
            self.dssLines.Next

        return line_name_list, line_length_list

    # ---------- GET CIRCUIT LOADS ----------
    # Função que retorna a lista de cargas do circuito
    def get_all_load_names(self):
        return self.dssLoads.AllNames

    # ---------- GET CIRCUIT LOADS ----------
    # Função que retorna a lista de cargas do circuito
    def get_all_loadshapes_names(self):
        return self.dssLoadShapes.AllNames

    # ---------- GET CIRCUIT TRAFO ----------
    # Função que retorna o nome do transformador
    def get_transformer_name(self):
        return self.dssTransformers.Name

    # Função que retorna a tensão de um dos enrolamentos do transformador
    def get_transformer_voltage_terminal(self, terminal_name):
        # Ativar o terminal do transformador
        self.dssTransformers.Wdg = terminal_name
        return self.dssTransformers.kV

    # ---------- SET CIRCUIT BUS ----------
    # Função que ativa uma barra pelo nome
    def set_active_bus(self, bus_name):
        self.dssCircuit.SetActiveBus(bus_name)

    # ---------- SET CIRCUIT ELEMENT ----------
    # Função que ativa elemento pelo seu nome completo Type.name
    def set_active_element(self, element_name):
        self.dssCircuit.SetActiveElement(element_name)
        return self.dssCktElement.Name

    # ---------- SET CIRCUIT LINES ----------
    # Função que altera a distância da linha
    def set_line_length(self, line_length):
        self.dssLines.Length = line_length

    # ---------- SET CIRCUIT LOADSHAPE ----------
    def set_new_loadshape(self, loadshape_name):
        self.dssLoadShapes.New(loadshape_name)
