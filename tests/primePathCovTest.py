from src.test import Test

class PrimePathCovTest(Test):
    def __init__(self, graph=None):
        super().__init__("PPC Test")
        self.graph = graph
        # Variables and modifiable parameters

    """
        Overrides the parent run method
    """
    def run(self):
        print("Running " + self.name + ".")
        # Do something with the generated graph