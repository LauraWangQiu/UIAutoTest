from src.test import Test

class TotalConnectTest(Test):
    def __init__(self, graph=None):
        super().__init__("TC Test")
        self.graph = graph
        self.visited_nodes = set()
        self.visited_transitions = set()

    """
        Overrides the parent run method
    """
    def run(self):
        print("Running " + self.name + ".")
        # Do something with the generated graph
