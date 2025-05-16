from test import Test

class TotalConnectTest(Test):
    def __init__(self, graph=None, graph_file=None):
        super().__init__("TC Test", graph, graph_file)
        self.visited_states = set()
        self.visited_transitions = set()

    """
        Overrides the parent run method
    """
    def run(self):
        print("Running " + self.name + ".")
        self.visited_states.clear()
        self.visited_transitions.clear()

        for node in self.graph.nodes:
            self.visited_states.add(node)
            for transition in node.transitions:
                self.visited_transitions.add(transition)
                self.visited_states.add(transition.destination)

        self.write_solution()

    """
        Overrides the parent write_solution method
    """
    def write_solution(self):
        try:
            with open(self.graph_file, "a") as file:
                file.write("[TOTAL CONNECTIVITY TEST]\n")
                file.write("[NON-VISITED NODES] \n")
                if len(self.visited_states) == len(self.graph.nodes):
                    file.write("There are not non-visited nodes\n")
                    pass
                else:
                    for node in self.graph.nodes:
                        if node not in self.visited_states:
                            file.write("[NODE NOT VISITED] " + node.name + "\n")
                file.write("[NON-VISITED TRANSITIONS]\n")
                aux = 0
                for node in self.graph.nodes:
                    for transition in node.transitions:
                        if transition not in self.visited_transitions:
                            aux += 1
                            file.write("[TRANSITION NOT VISITED] " + node.name + "-" + transition.destination + "\n")
                if aux == 0:
                    file.write("There are not non-visited transitions\n")

        except Exception as e:
            print("[ERROR] Exception while writing test data from: " + self.name + ": " + str(e))
        else:
            print("[INFO] Test data from: " + self.name + " successfully written to " + self.graph_file)
