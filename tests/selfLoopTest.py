from test import Test

class SelfLoopTest(Test):
    def __init__(self, graph=None, graph_file=None):
        super().__init__("SP Test", graph, graph_file)
        self.selfLoopList = set()
        self._update_callback = None

    """
        Overrides the parent run method
    """
    def run(self):
        print("Running " + self.name + ".")
        for node in self.graph.nodes:
            # See all the transitions of the node
            for transitions in node.transitions:
                # If the destination is the same node
            
                if transitions.destination is node:
                    print("SelfLoop in node: " + node.name)
                    self.selfLoopList.add(node)
                    break
                else:
                    print("Not SelfLoop")

        content = "\n".join(node.name for node in self.selfLoopList)
        self.notify_update("selfLoopList", content)
        self.write_solution()

    def write_solution(self):
        try:
            with open(self.graph_file, "a") as file:
                file.write("[SELF LOOP TEST]\n")
                if not self.selfLoopList:
                    file.write("No self loops found\n")
                else:
                    for node in self.selfLoopList:
                        file.write("[SELF LOOP NODE ] " + node.name + "\n")   
        except Exception as e:
            print("[ERROR] Exception while writing test data from: " + self.name + ": " + str(e))
        else:
            print("[INFO] Test data from: " + self.name + " successfully written to " + self.graph_file)
