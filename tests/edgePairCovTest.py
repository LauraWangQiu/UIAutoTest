from test import Test

class EdgePairCovTest(Test):
    def __init__(self, graph=None):
        super().__init__("EPC Test")
        self.graph = graph
        self.EdgePairCovList = set()   #Dictionary of duplicated edges
        # Variables and modifiable parameters
    
    """
        Overrides the parent run method
    """
    def run(self):
        print("Running " + self.name + ".")
        for node in self.graph.nodes:
            edge_count = {}
            for transitions in node.transitions:
                dest_name = transitions.destination.name #Destination of the node
                edge_count[dest_name] = edge_count.get(dest_name, 0) + 1

            for dest_name, count in edge_count.items():
                if count > 1:
                    if (node.name, dest_name) not in self.EdgePairCovList:
                        self.EdgePairCovList.add((node.name, dest_name))
                        print(f"Multiple transitions ({count}) from '{node.name}' to '{dest_name}'")

        if not self.EdgePairCovList:
            print ("La lista está vacia")
        else:
            for origin, dest in self.EdgePairCovList:
                print(F"- From '{origin}' to '{dest}' has multiple transitions\n")

    def write_solution(self, graph_file):
        try:
            with open(graph_file, "w") as file:
                file.write("Edge Pair Cov Test:\n")
                # Write the results of the test
                if not self.EdgePairCovList:
                    file.write ("La lista está vacia\n")
                else:
                    for origin, dest in self.EdgePairCovList:
                        file.write(F"- From '{origin}' to '{dest}' has multiple transitions\n")
        except Exception as e:
            print("[ERROR] Exception while writing test data from: " + self.name + ": " + str(e))
        else:
            print("[INFO] Test data from: " + self.name + " successfully written to " + graph_file)
