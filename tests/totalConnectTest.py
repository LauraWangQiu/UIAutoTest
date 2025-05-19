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
        for node in self.graph.nodes:
            self.visited_states.add(node)
            for transition in node.transitions:
                self.visited_transitions.add((node.name, transition.destination.name))
                self.visited_states.add(transition.destination)

        content = "\n".join(node.name for node in self.visited_states)
        self.notify_update("visited_states", content)
        content = "\n".join(f"{origin} → {dest}" for origin, dest in self.visited_transitions)
        self.notify_update("visited_transitions", content)

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
                        if (node.name, transition.destination.name) not in self.visited_transitions:
                            aux += 1
                            file.write("[TRANSITION NOT VISITED] " + node.name + "-" + transition.destination.name + "\n")
                if aux == 0:
                    file.write("There are not non-visited transitions\n")

        except Exception as e:
            print("[ERROR] Exception while writing test data from: " + self.name + ": " + str(e))
        else:
            print("[INFO] Test data from: " + self.name + " successfully written to " + self.graph_file)
            
    def get_results(self):
        nodes = { node.name for node in self.visited_states}
        result = ['TCT', [nodes, self.visited_transitions]]
        return result
