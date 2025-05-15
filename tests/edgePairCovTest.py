from src.test import Test

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
        # Do something with the generated graph

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
