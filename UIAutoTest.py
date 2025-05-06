from src.app import App

window_name = "UIAutoTest"
window_size = "800x600"
tests_directory = "tests"

if __name__ == "__main__":
    app = App(window_name=window_name, window_size=window_size, tests_directory=tests_directory)
    app.mainloop()
