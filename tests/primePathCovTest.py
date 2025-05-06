from src.test import Test

class PrimePathCovTest(Test):
    def __init__(self, selected_executable=None):
        super().__init__("PPC Test", selected_executable)
        # Variables and modifiable parameters

    def run(self):
        super().run()
        # ...

    def on_graph_step(self, element):
        print(f"Element: {element}")
        # ...
