from src.test import Test

class Test_Self_Loop(Test):

    def __init__(self):
        super().__init__("Self Loop")
        print("Test Self Loop initialized")

    def run(self):
        print("Running Self Loop logic")
        # More logic here