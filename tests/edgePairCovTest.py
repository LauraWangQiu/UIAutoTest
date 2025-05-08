from src.test import Test

class EdgePairCovTest(Test):
    def __init__(self, selected_executable=None):
        super().__init__("EPC Test", selected_executable)
        self.EdgePairCovList = {}   #Dictionary of duplicated edges
        # Variables and modifiable parameters

    def run(self):
        super().run()
        # ...

    def on_graph_step(self, element):
        print(f"Element: {element}")
        
         # It is a node
        if hasattr(element, "name"):
            edge_count = {}
            for transition in element.transitions:
                dest_name = transition.destination.name #Destination of the node
                edge_count[dest_name] = edge_count.get(dest_name, 0) + 1

            for dest_name, count in edge_count.items():
                if count > 1:
                    if (element.name, dest_name) not in self.EdgePairCovList:
                        self.EdgePairCovList[(element.name, dest_name)] = count
                        print(f"Multiple transitions ({count}) from '{element.name}' to '{dest_name}'")
       