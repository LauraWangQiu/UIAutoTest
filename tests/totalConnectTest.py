from src.test import Test

class TotalConnectTest(Test):
    def __init__(self, selected_executable=None):
        super().__init__("TC Test", selected_executable)
        self.visited_nodes = set()
        self.visited_transitions = set()

    def run(self):
        super().run()
        print(f"{self.name}: Visited nodes: {self.visited_nodes}")
        print(f"{self.name}: Visited transitions: {self.visited_transitions}")

    def on_graph_step(self, element):
        # It is a node
        if hasattr(element, "name"):
            self.visited_nodes.add(element.name)
        # It is a transition
        elif hasattr(element, "destination"):
            self.visited_transitions.add((element.source.name, element.destination.name))