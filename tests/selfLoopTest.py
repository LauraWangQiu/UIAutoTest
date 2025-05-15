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

        for node in self.graph.nodes:
            #See all the transitions of the node
            for transitions in node.transitions:
                #If the destination is the same node
                if transitions.destination is node:
                    print("SelfLoop in node: {node.name}")
                    self.selfLoopList(node)
                    break
                else: print("Nop SelfLoop")

        