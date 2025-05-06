from src.test import Test

class EdgePairCovTest(Test):
    def __init__(self, selected_executable=None):
        super().__init__("EPC Test", selected_executable)
        # Variables and modifiable parameters

    def run(self):
        super().run()
        # ...

    def on_graph_step(self, element):
        print(f"Element: {element}")
        # ...