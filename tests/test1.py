from src.test import Test

class Test1(Test):
    def __init__(self):
        super().__init__("Total Connectivity")
        print("Test1 initialized")

    def run(self):
        print("Running Test1 logic")
        # More logic here