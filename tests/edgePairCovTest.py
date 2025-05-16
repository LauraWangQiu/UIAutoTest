from test import Test

class EdgePairCovTest(Test):
    def __init__(self, graph=None, graph_file=None):
        super().__init__("EPC Test", graph, graph_file)
        self.EdgePairCovList = set()   # Dictionary of duplicated edges
        self._update_callback = None

    
    """
        Overrides the parent run method
    """
    def run(self):
        print("Running " + self.name + ".")
        self.EdgePairCovList.clear()
        for node in self.graph.nodes:
            edge_count = {}
            for transitions in node.transitions:
                dest_name = transitions.destination.name # Destination of the node
                edge_count[dest_name] = edge_count.get(dest_name, 0) + 1

            for dest_name, count in edge_count.items():
                if count > 1:
                    if (node.name, dest_name) not in self.EdgePairCovList:
                        self.EdgePairCovList.add((node.name, dest_name))
                        print(f"Multiple transitions ({count}) from '{node.name}' to '{dest_name}'")
                
        content = "\n".join(f"From '{origin}' to '{dest}'" for origin, dest in self.EdgePairCovList)
        self.notify_update("EdgePairCovList", content)
        self.write_solution()

    def set_update_callback(self, callback):
        self._update_callback = callback

    def notify_update(self, attr_name, content):
        if self._update_callback:
            self._update_callback(attr_name, content)

    def write_solution(self):
        try:
            with open(self.graph_file, "a") as file:
                file.write("[EDGE PAIR COVERAGE TEST]\n")
                # Write the results of the test
                if not self.EdgePairCovList:
                    file.write("No edge pairs found\n")
                else:
                    for origin, dest in self.EdgePairCovList:
                        file.write(F"- From '{origin}' to '{dest}' has multiple transitions\n")
        except Exception as e:
            print("[ERROR] Exception while writing test data from: " + self.name + ": " + str(e))
        else:
            print("[INFO] Test data from: " + self.name + " successfully written to " + self.graph_file)
