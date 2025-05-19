"""
    This class is a base class for all tests.
"""
class Test:
    def __init__(self, name="Parent Test Class", graph=None, graph_file=None):
        self.name = name
        self.graph = graph
        self.graph_file = graph_file
        self._update_callback = None
        print(f"[INFO] Initializing {self.name} class.")

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
    
    """
        Method to update the callback.
    """
    def set_update_callback(self, callback):
        self._update_callback = callback

    """
        Method to notify the update of the test.
    """
    def notify_update(self, attr_name, content):
        if self._update_callback:
            self._update_callback(attr_name, content)
            
    def get_results(self):
        pass