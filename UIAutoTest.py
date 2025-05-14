# -*- coding: utf-8 -*-
import sys
from src.app import App

window_name = "UIAutoTest"
window_size = "800x600"
tests_directory = "tests"

if __name__ == "__main__":
    
    headless_mode = len(sys.argv) > 1 and sys.argv[1].lower() == "headless"

   
    app = App(window_name=window_name, window_size=window_size, tests_directory=tests_directory, headless=headless_mode)
    if not headless_mode:
        app.mainloop()
