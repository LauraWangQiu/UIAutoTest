import subprocess
import os
import shutil
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
        self.file_output = "output.txt"
        os.makedirs(self.screenshot_dir, exist_ok=True)  # Create the directory if it doesn't exist

    """
        Compare two graphs and return True if they are equal, False otherwise.
    """
    def compare_graphs(self, graph1, graph2):
        #if DEBUG:
        #    print("[DEBUG] Comparing graphs...")
        #    graph1 = GraphIO.read_graph("graph1.json")
        #else:
        #    print("[INFO] Comparing graphs...")
        #    generated_graph = GenerateGraph.generate_graph(self.graph)

        if len(graph1) != len(graph2):
            return False

        for node1 in graph1.nodes:
            if graph2.is_node_in_graph_image(node1.image):
                for trans1 in node1.transitions, node2.transitions:
                    if trans1.destination is not in node2.transitions:
                    self.file_output.write(f"Transition {trans1} not found in graph2.\n")
            else:
                return False
        
        self.execute_tests()

        return True
        
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