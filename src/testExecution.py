import os
import time
from test import Test
from graphsDef import Graph, Node, Transition
import GraphIO as _graph_io_module
GraphIO = _graph_io_module.GraphIO

class TestExecution:
    """
    Class to execute tests based on a graph structure.
    It uses SikuliX for image recognition and interaction.
    """

    def __init__(self):
        self.test_to_execute = []
        self.differences_found = 0
        self.file_output = "bin/output.txt"
        #os.makedirs(self.screenshot_dir, exist_ok=True)  # Create the directory if it doesn't exist

    """
        Compare two graphs and return True if they are equal, False otherwise.
    """
    def compare_graphs(self, graph1, graph2):  
        print("[INFO] Comparing graphs.")
        self.file_output = open(test.file_output, "w")   
        self.differences_found = 0  # differences found
        if graph1 is None or graph2 is None:
            self.file_output.write("[ERROR] One of the graphs is None.")
            return False         
            
        self.file_output.write("[COMPARING GENERATED GRAPH vs GIVEN GRAPH]\n")
        self.compare_aux(graph1, graph2)
        
        self.file_output.write("[COMPARING GIVEN GRAPH vs GENERATED GRAPH]\n")
        self.compare_aux(graph2, graph1)

        print("[INFO] Graph comparison finished. " + str(self.differences_found) + " differences found.")
        if self.differences_found == 0:
            print("[INFO] No differences found.")
            self.file_output.write("[NO DIFFERENCES FOUND]\n")
        
        self.execute_tests()
        return True

    """
        Compare two graphs.
    """
    def compare_aux(self, graph1, graph2):
        for node1 in graph1.nodes:
            print("[INFO] Comparing node: " + node1.name)
            node2 = graph2.get_node_image(node1.image)
            if node2 is None: # Node is not in generated graph
                print("[INFO] Node not found: " + node1.name)
                self.file_output.write("[MISSING NODE] " + node1.name + " not in graph2\n")
                self.differences_found += 1
                continue

            for trans1 in node1.transitions:
                dest_image = trans1.destination.image
                found = False
                
                for trans2 in node2.transitions:
                    print("[INFO] Comparing transition: " + trans1.image)
                    if trans2.image == trans1.image:
                        print("[INFO] Transition found: " + trans1.image)
                        if trans2.destination.image != dest_image:
                            print("[INFO] Transition mismatch: " + trans1.image)
                            # Writes the objetive destination and the real destination
                            self.file_output.write("[MISMATCH TRANSITION] Supposed: " + node1.name + " -/-> " + trans1.destination.name + " Real: " + node1.name +" -> " + trans2.destination.name + "\n")
                            self.differences_found += 1
                        found = True
                        continue
                if not found:
                    print("[INFO] Transition not found: " + trans1.image)
                    self.file_output.write("[MISSING TRANSITION] " + node1.name + " -/-> " + trans1.destination.name + "\n")
                    self.differences_found += 1
    """
        Adds a test to the list of tests to be executed
    """
    def add_test_to_Execute(self, test):
        if test not in self.test_to_execute:
            self.test_to_execute.append(test)
            
    def add_tests_to_Execute(self, tests_list):
        self.test_to_execute = tests_list
    
    """
        Execute all tests in the graph.
    """
    def execute_tests(self):
        for test in self.test_to_execute:
            if isinstance(test, Test):
                test.run()
                test.write_solution(self.file_output)
            else:
                print(f"Test {test} is not a valid Test instance.")

# EXAMPLE OF USAGE
# 
# if __name__ == "__main__":
#    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Obtain the base path
#    img_path = os.path.join(base_path, "imgs") 
#    given_graph_path = os.path.join(base_path, "src\generated_graph_test.txt")
#    generated_graph_path = os.path.join(base_path, "src\given_graph_test.txt") 
#    graph_io = GraphIO() 
#    given_graph = graph_io.load_graph(given_graph_path, img_path)
#    generated_graph = graph_io.load_graph(generated_graph_path, img_path)
#    test.compare_graphs(generated_graph, given_graph)