from app import App

import time

"""
    Console class for running the application in a headless mode.
"""
class Console(App):
    def __init__(self,
                java_path, sikulix_jar,
                sikuli_script,
                images_dir, tests_dir, 
                theorical_graph_file,
                practical_graph_file,
                generate_graph,
                selected_executable,
                executable_delay,
                transition_delay,
                debug_images,
                timeout,
                initial_similarity,
                min_similarity,
                similarity_step,
                retries,
                state_reset_method,
                external_reset_script,
                tests_to_run,
                solution_file,
                pdf_file):
        
        App.__init__(self=self,
            java_path=java_path,
            sikulix_jar=sikulix_jar,
            sikuli_script=sikuli_script,
            images_dir=images_dir,
            tests_dir=tests_dir,
            theorical_graph_file=theorical_graph_file,
            practical_graph_file=practical_graph_file,
            selected_executable=selected_executable,
            executable_delay=executable_delay,
            transition_delay=transition_delay,
            debug_images=debug_images,
            timeout=timeout,
            initial_similarity=initial_similarity,
            min_similarity=min_similarity,
            similarity_step=similarity_step,
            retries=retries,
            state_reset_method=state_reset_method,
            external_reset_script=external_reset_script,
            tests_to_run=tests_to_run,
            solution_file=solution_file,
            pdf_file=pdf_file)
        
        self.generate_graph = generate_graph
       
        print("[INFO] Application initialized without window")
        if self.load_graph_from_file(self.theorical_graph_file):
            self.test_classes = self.get_test_classes()
            if generate_graph:
                if self.generate_graph_from_executable():
                    while self.jython_thread.is_alive():
                        time.sleep(0.1)
            self.run_tests()
            self.compare()
            self.create_PDF(self.pdf_file)     
        
    """
        Returns the selected test classes for run the test.
    """   
    def get_selected_test_classes(self):
        selected_test_classes = []
        if self.test_classes is not None:
            available_test_classes = {name: ref for name, ref in self.test_classes}
            for test_name in self.tests_to_run:
                if test_name in available_test_classes:
                    selected_test_classes.append(available_test_classes[test_name])
                else:
                    print(f"[ERROR] Test class '{test_name}' not found in available test classes.")
        return selected_test_classes   
