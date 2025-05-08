from src.test import Test

class SelfLoopTest(Test):
    def __init__(self, graph=None):
        super().__init__("SP Test")
        self.graph = graph
        self.selfLoopList = set()

    """
        Overrides the parent run method
    """
    def run(self):
        print("Running " + self.name + ".")
        # Do something with the generated graph
        