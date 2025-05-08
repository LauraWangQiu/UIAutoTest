from src.test import Test

class SelfLoopTest(Test):
    def __init__(self, selected_executable=None):
        super().__init__("SP Test", selected_executable)
        self.selfLoopList = set()

    def run(self):
        super().run()
        print(f"{self.name}: Self loops: {self.selfLoopList}")

    def on_graph_step(self, element):
        print(f"Element: {element}")

        # It is a node
        if hasattr(element, "name"):
            #See all the transitions of the node
            for transition in element.transitions:
                if transition.destination is element:      #If the destination is the same node
                    print("SelfLoop in node: {element.name}")   
                    self.selfLoopList(element)
                    break

        # It is a transition
        #elif hasattr(element, "destination"):

        