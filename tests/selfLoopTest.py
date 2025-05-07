from src.test import Test

class SelfLoopTest(Test):
    def __init__(self, selected_executable=None):
        super().__init__("SP Test", selected_executable)
        self.selfLoopList = set()
        # TO REMOVE
        self.selfLoopList.add("selfLoop")
        self.selfLoopList.add("selfLoop2")

    def run(self):
        super().run()
        print(f"{self.name}: Self loops: {self.selfLoopList}")

    def on_graph_step(self, element):
        print(f"Element: {element}")

        for node in self.graph.nodes:
            for transition in node.transitions:
                if transition.destination is node:      #If the destination is the same node
                    print("SelfLoop in node: {node.name}")   
                    self.selfLoopList(node)
                    break