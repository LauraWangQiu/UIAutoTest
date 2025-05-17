from test import Test

class EdgePairCovTest(Test):
    def __init__(self, graph=None, graph_file=None):
        super().__init__("EPC Test", graph, graph_file)
        self.edgePairCovList = set()   # Dictionary of duplicated edges

    """
        Overrides the parent run method
    """
    def run(self):
        print("Running " + self.name + ".")
        for node in self.graph.nodes:
            edge_count = {}
            for transitions in node.transitions:
                dest_name = transitions.destination.name # Destination of the node
                edge_count[dest_name] = edge_count.get(dest_name, 0) + 1

            for dest_name, count in edge_count.items():
                if count > 1:
                    if (node.name, dest_name) not in self.edgePairCovList:
                        self.edgePairCovList.add((node.name, dest_name))
                        print(f"Multiple transitions ({count}) from '{node.name}' to '{dest_name}'")
        
        content = "\n".join(f"From '{origin}' to '{dest}'" for origin, dest in self.edgePairCovList)
        self.notify_update("edgePairCovList", content)

    def write_solution(self):
        try:
            with open(self.graph_file, "a") as file:
                file.write("[EDGE PAIR COVERAGE TEST]\n")
                # Write the results of the test
                if not self.edgePairCovList:
                    file.write("No edge pairs found\n")
                else:
                    for origin, dest in self.edgePairCovList:
                        file.write(F"- From '{origin}' to '{dest}' has multiple transitions\n")
        except Exception as e:
            print("[ERROR] Exception while writing test data from: " + self.name + ": " + str(e))
        else:
            print("[INFO] Test data from: " + self.name + " successfully written to " + self.graph_file)
