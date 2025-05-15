from test import Test

class TotalConnectTest(Test):
    def __init__(self, graph = None, graph_file = "output_graph.txt"):
        super().__init__("TC Test", "output_graph.txt")
        self.graph = graph
        self.graph_f = graph_file 
        # Variables and modifiable parameters:
        self.visited_states = set()
        self.visited_transitions = set()

    """
        Overrides the parent run method
    """
    def run(self):
        print("Running " + self.name + ".")
        # self.visited_states.clear()
        # self.visited_transitions.clear()
        # # Do something with the generated graph:
        # self.execute_test()
        # self.write_solution(self.graph_f)

    # Total Connectivity Test:
    def execute_test(self):
        self.visit_nodes(self.graph.startNode)

    # Visit all the nodes from node.
    def visit_nodes(self, node):
        if node in self.visited_states:
            return

        self.visited_states.add(node)

        for transition in node.transitions:
           if transition not in self.visited_transitions:
               self.visited_transitions.add(transition)
               if transition.is_valid():
                   self.visit_nodes(transition.destination)
    
    """
        Overrides the parent write_solution method
    """
    # TODO: PAIGRO HERE.
    def write_solution(self, graph_file):
        try:
            with open(graph_file, "w") as file:
                file.write("Total Connectivity Test:\n")
                # Nodes.
                if len(self.visited_states) == len(self.graph.nodes):
                    file.write("--There are no non-visited nodes.")
                    pass
                else:
                    file.write("--Non-visited nodes: \n")
                    for node in self.graph.nodes:
                        if node not in self.visited_states:
                            file.write(node.name + "\n")
                # Transitions.
                file.write("--Non-visited transitions: \n")
                aux: 0
                for node in self.graph.nodes:
                    for transition in node:
                        if transition not in self.visited_transitions:
                            aux += 1
                            file.write("Transition: " + node.name + "-" + transition.destination)
                if aux == 0:
                    file.write("--There are no non-visited transitions.")

        except Exception as e:
            print("[ERROR] Exception while writing test data from: " + self.name + ": " + str(e))
        else:
            print("[INFO] Test data from: " + self.name + " successfully written to " + graph_file)