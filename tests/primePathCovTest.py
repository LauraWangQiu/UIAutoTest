from test import Test

class PrimePathCovTest(Test):
    def __init__(self, graph=None, graph_file=None):
        super().__init__("PPC Test", graph, graph_file)
        self.prime_paths = set()
        self._update_callback = None


    """
        Overrides the parent run method
    """
    def run(self):
        print("Running " + self.name + ".")
        self.prime_paths.clear()
        
        all_paths = []

        # Get all the paths
        for node in self.graph.nodes:
            self.dfs(node, set(), [], all_paths) # POR QUE?
        
        # Filter and keep the prime paths only
        for referencePath in all_paths:
            prime = True

            for otherPath in all_paths:
                if referencePath != otherPath:
                    if self.is_subpath(referencePath, otherPath):
                        prime = False
                        break
            if prime:
                self.prime_paths.add(tuple(referencePath))

        
        content = "".join(" → ".join(node.name for node in path) for path in self.prime_paths)
        self.notify_update("prime_paths", content)
        self.write_solution()
    
    def set_update_callback(self, callback):
        self._update_callback = callback

    def notify_update(self, attr_name, content):
        if self._update_callback:
            self._update_callback(attr_name, content)
        
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
    def write_solution(self):
        try:
            with open(self.graph_file, "a") as file:
                file.write("[PRIME PATH COVERAGE TEST]\n")
                for path in self.prime_paths:
                    file.write("[PRIME PATH] ")
                    file.write(" -> ".join(node.name for node in path))
        except Exception as e:
            print("[ERROR] Exception while writing test data from: " + self.name + ": " + str(e))
        else:
            print("[INFO] Test data from: " + self.name + " successfully written to " + self.graph_file)
