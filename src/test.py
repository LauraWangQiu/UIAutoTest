"""
    This class is a base class for all tests.
"""
class Test:
    def __init__(self, name="Parent Test Class", graph_file = "output_graph.txt"):
        self.name = name
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
