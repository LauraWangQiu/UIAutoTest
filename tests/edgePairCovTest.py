from src.test import Test

class EdgePairCovTest(Test):
    def __init__(self, graph=None):
        super().__init__("EPC Test")
        self.graph = graph
        self.EdgePairCovList = {}   #Dictionary of duplicated edges
        # Variables and modifiable parameters
    
    """
        Overrides the parent run method
    """
    def run(self):
        print("Running " + self.name + ".")
        # Do something with the generated graph
