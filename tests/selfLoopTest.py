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
        # ...