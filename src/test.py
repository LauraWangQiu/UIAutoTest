"""
    This class is a base class for all tests.
"""
class Test:
    def __init__(self, name="Parent Test Class", graph=None, graph_file=None):
        self.name = name
        self.graph = graph
        self.graph_file = graph_file
        print(f"Initializing {self.name} class.")

    """
        Returns the name of the test.
    """
    def get_name(self):
        return self.name

    """
        Method to be implemented by subclasses.
    """
    def run(self):
        pass  
    
    """
        Method print to be implemented by subclasses.
    """
    def write_solution(self):
        pass
