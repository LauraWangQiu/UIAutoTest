from src.test import Test

class TotalConnectTest(Test):
    def __init__(self, graph = None, graph_file = "output_graph.txt"):
        super().__init__("TC Test", "output_graph.txt")
        self.graph = graph
        self.graph_f = graph_file 
        # Variables and modifiable parameters:
        self.visited_nodes = set()
        self.visited_transitions = set()

    """
        Overrides the parent run method
    """
    def run(self):
        print("Running " + self.name + ".")
        self.visited_nodes.clear()
        self.visited_transitions.clear()
        # Do something with the generated graph:
        self.execute_test()
        self.write_solution()

    # Total Connectivity Test:
    def execute_test(self):
        self._visit_nodes(self.graph.startNode)

    # Visit all the nodes from node.
    def _visit_nodes(self, node):
        if node in self.visited_nodes:
            return

        self.visited_nodes.add(node)

        for transition in node.transitions:
           if transition not in self.visited_transitions:
               self.visited_transitions.add(transition)
               if transition.is_valid():
                   self._visit_nodes(transition.destination)
    
    """
        Overrides the parent write_solution method
    """
    # TODO: PAIGRO HERE.
    def write_solution(self, graph_file):
        try:
            with open(graph_file, "w") as file:
                file.write("Total Connectivity Test:\n")
        except Exception as e:
            print("[ERROR] Exception while writing test data from: " + self.name + ": " + str(e))
        else:
            print("[INFO] Test data from: " + self.name + " successfully written to " + graph_file)