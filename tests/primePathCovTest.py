from test import Test

class PrimePathCovTest(Test):
    def __init__(self, graph = None, graph_file = "output_graph.txt"):
        super().__init__("PPC Test", "output_graph.txt")
        self.graph = graph
        self.graph_f = graph_file 
        # Variables and modifiable parameters:
        self.prime_paths = set()

    """
        Overrides the parent run method
    """
    def run(self):
        print("Running " + self.name + ".")
        # self.prime_paths.clear()
        # # Do something with the generated graph:
        # self.execute_test()
        # self.write_solution(self.graph_f)
        
    # Prime Path Coverage Test:
    def execute_test(self):
        all_paths = []

        # Get all the paths
        for node in self.graph.nodes:
            self.dfs(node, set(), [], all_paths)
        
        # Filter and keep the prime paths only.
        for referencePath in all_paths:
            prime = True

            for otherPath in all_paths:
                if referencePath != otherPath:
                    if self.is_subpath(referencePath, otherPath):
                        prime = False
                        break
            if prime:
                self.prime_paths.add(referencePath)

    # DFS method to get all the paths.
    def dfs(self, current, visited, path, all_paths):
        visited.add(current)
        path.append(current)

        for transition in current.transitions:
            next_node = transition.destination
            if next_node not in visited:
                self.dfs(next_node, visited.copy(), path.copy(), all_paths)
            elif next_node == path[0]:
                all_paths.append(path + [next_node])

        all_paths.append(path)

    # Checks if the possibleSubPath is a sub-path of the referencePath.
    def is_subpath(self, posibleSubPath, referencePath):
        # If the possible is bigger than the reference then it is not a sub-path.
        if len(posibleSubPath) > len(referencePath):
            return False
        # Checks if the nodes in reference are in the posible.
        for i in range(len(referencePath) - len(posibleSubPath) + 1):
            match = True
            for j in range(len(posibleSubPath)):
                if referencePath[i + j] != posibleSubPath[j]:
                    match = False
                    break
            if match:
                return True
        return False

    """
        Overrides the parent write_solution method
    """
    # TODO: PAIGRO HERE.
    def write_solution(self, graph_file):
        try:
            with open(graph_file, "w") as file:
                file.write("Prime Path Coverage Test:\n")
                for path in self.prime_paths:
                    file.write("[")
                    file.write(", ".join(node.name for node in path))
                    file.write("]\n")
        except Exception as e:
            print("[ERROR] Exception while writing test data from: " + self.name + ": " + str(e))
        else:
            print("[INFO] Test data from: " + self.name + " successfully written to " + graph_file)