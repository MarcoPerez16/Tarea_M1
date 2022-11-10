import random
import mesa


def puerto_agente(agente):

    representacion = {
        "Shape": "circle",
        "Filled": "true",
        "Layer": "aspiradora",
        "Color": "red",
        "r": 0.5,
    }

    if type(agente) == Agente_Basura:
        representacion["Color"] = "red"
    else:
        representacion["Color"] = "blue"

    if type(agente) == Agente_Basura and agente.cantidad != True:
        representacion["Color"] = "green"

    return representacion


def calcular_gini(model):
    agentes = [agent.wealth for agent in model.schedule.agents]
    x = sorted(agentes)
    N = model.num
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return 1 + (1 / N) - 2 * B


class Agente_Basura(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.cantidad = True
        self.wealth = 1

    def step(self):
        c = 0
        c += 1


class Agente_Aspiradora(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = 1

    def move(self):
        posibles_pasos = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        nueva_pos = self.random.choice(posibles_pasos)
        self.model.grid.move_agent(self, nueva_pos)

    def step(self):
        self.move()

        cell = self.model.grid.get_cell_list_contents([self.pos])
        for i in cell:
            if type(i) == Agente_Basura and i.cantidad == True:
                self.model.grid.remove_agent(i)
                self.wealth += 1


class Ambiente(mesa.Model):
    def __init__(self, N, T):
        self.num = N
        self.num2 = T
        self.grid = mesa.space.MultiGrid(10, 10, False)
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True
        for i in range(self.num):
            agente_aspiradora = Agente_Aspiradora(i, self)
            self.schedule.add(agente_aspiradora)
            self.grid.place_agent(agente_aspiradora, (1, 1))

        for i in range(self.num2):
            basura = Agente_Basura(self.num+i, self)
            self.schedule.add(basura)
            x = random.randint(0, 9)
            y = random.randint(0, 9)
            self.grid.place_agent(basura, (x, y))

        self.datacollector = mesa.DataCollector(
            model_reporters={"Gini": calcular_gini}, agent_reporters={"Wealth": "wealth"}
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()


grid = mesa.visualization.CanvasGrid(puerto_agente, 10, 10, 500, 500)
chart = mesa.visualization.ChartModule([{"Label": "Gini",
                                         "Color": "green"}],
                                       data_collector_name='datacollector')
server = mesa.visualization.ModularServer(
    Ambiente, [grid, chart], "aspiradora", {"N": 6, "T": 9}
)
server.port = 6961
server.launch()
