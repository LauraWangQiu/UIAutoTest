# -*- coding: utf-8 -*-
import os
from org.python.core import PySystemState

py_sys = PySystemState()
py_sys.path.append("sikulixapi-2.0.5.jar")

from org.sikuli.script import Screen, Pattern, Key, KeyModifier, Region

"""
Decorator to turn a class into a Singleton.
Ensures only one instance of the class is ever created.
"""
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

"""
    Wrapper around SikuliX's Screen object, implemented as a Singleton.
    Provides convenient methods to search for and click images,
    as well as to capture screenshots on error.
"""
@singleton
class SikulixWrapper:
    def __init__(self):
        self.screen = Screen()
        self.last_match_region = None

    """
    Attempt to locate the given image on screen several times.

    :param image_path: Path to the image file to search for.
    :param similarity: Starting similarity threshold (0.0–1.0).
    :param timeout: How many seconds to wait on each try.
    :param retries: Number of attempts before giving up.
    :param similarity_reduction: Amount to reduce similarity per attempt.
    :return: True if the image was found; False otherwise.
    """
    def search_image(self, image_path, similarity=1.0, timeout=2, retries=6, similarity_reduction=0.1, debug_image_name= "debug_image", debug_image_path=".", capture_last_match=False):
        print("[INFO] Searching for image: " + image_path)
        for attempt in range(retries):
            actual_attempt = attempt + 1
            actual_similarity = similarity - (similarity_reduction*attempt)
            print("Attempts " + str(actual_attempt) + "/" + str(retries))
            match = self.screen.exists(Pattern(image_path).similar(actual_similarity), timeout)
            if match:
                self.last_match_region = (match.getX(), match.getY(), match.getW(), match.getH())
                if capture_last_match:
                    self.capture_error(debug_image_name, debug_image_path, capture_last_match)
                print("[OK] Image found.")
                return True
            else:
                print("[WARNING] Not found. Trying again...")

        return False
    
    """
        Search for an image on the screen once.

        :param image_path: Path to the image file to search for.
        :param similarity: Similarity threshold (0.0–1.0).
        :param timeout: How many seconds to wait.
        :return: True if the image was found; False otherwise.
    """
    def search_image_once(self, image_path, similarity=1.0, timeout=2):
        print("[INFO] Searching for image (once): " + image_path)
        match = self.screen.exists(Pattern(image_path).similar(similarity), timeout)
        if match:
            print("[OK] Image found.")
            return True
        else:
            print("[WARNING] Not found.")
            return False

    """
        Attempt to locate and click the given image on screen.

        :param image_path: Path to the image file to click.
        :param similarity: Starting similarity threshold (0.0–1.0).
        :param timeout: How many seconds to wait on each try.
        :param retries: Number of attempts before giving up.
        :param similarity_reduction: Amount to reduce similarity per attempt.
        :return: True if the click was successful; False otherwise.
    """
    def click_image(self, image_path, similarity=1.0, timeout=2, retries=6, similarity_reduction = 0.1, debug_image_name= "debug_image", debug_image_path=".", capture_last_match=False):
        print("[INFO] Trying click on image: " + image_path)
        for attempt in range(retries):
            actual_attempt = attempt + 1
            actual_similarity = similarity - (similarity_reduction*attempt)
            print("Attempts " + str(actual_attempt) + "/" + str(retries))
            match = self.screen.exists(Pattern(image_path).similar(actual_similarity), timeout)
            if match:
                self.last_match_region = (match.getX(), match.getY(), match.getW(), match.getH())
                if capture_last_match:
                    self.capture_error(debug_image_name, debug_image_path, capture_last_match)
                self.screen.click(Pattern(image_path).similar(actual_similarity))
                print("[OK] Clicked image.")
                return True
            else:
                print("[WARNING] Not found. Trying again...")

        return False
    
    """
        Attempt to locate and double-click the given image on screen.

        :param image_path: Path to the image file to click.
        :param similarity: Starting similarity threshold (0.0–1.0).
        :param timeout: How many seconds to wait on each try.
        :param retries: Number of attempts before giving up.
        :param similarity_reduction: Amount to reduce similarity per attempt.
        :return: True if the click was successful; False otherwise.
    """
    def double_click_image(self, image_path, similarity=1.0, timeout=2, retries=6, similarity_reduction=0.1, debug_image_name="debug_image", debug_image_path=".", capture_last_match=False):
        print("[INFO] Trying double click on image: " + image_path)
        for attempt in range(retries):
            actual_attempt = attempt + 1
            actual_similarity = similarity - (similarity_reduction * attempt)
            print("Attempts " + str(actual_attempt) + "/" + str(retries))
            match = self.screen.exists(Pattern(image_path).similar(actual_similarity), timeout)
            if match:
                self.last_match_region = (match.getX(), match.getY(), match.getW(), match.getH())
                if capture_last_match:
                    self.capture_error(debug_image_name, debug_image_path, capture_last_match)
                self.screen.doubleClick(Pattern(image_path).similar(actual_similarity))
                print("[OK] Double clicked image.")
                return True
            else:
                print("[WARNING] Not found. Trying again...")

        return False
    """
        Clicks on an image (e.g., input field) and types text into it.

        :param image_path: Path to the image of the target input field.
        :param text: The text to type.
        :param similarity: Starting similarity threshold.
        :param timeout: Time to wait per attempt.
        :param retries: Number of attempts before giving up.
        :param similarity_reduction: Amount to reduce similarity per attempt.
        :param clear_before: If True, clears the field before typing.
        :return: True if successful, False otherwise.
    """
    def write_text(self, image_path, text, similarity=1.0, timeout=2, retries=6, similarity_reduction=0.1, clear_before=False, debug_image_name= "debug_image", debug_image_path=".", capture_last_match=False, enter = True):
        for attempt in range(retries):
            actual_similarity = similarity - (similarity_reduction * attempt)
            actual_attempt = attempt + 1
            print("Attempts " + str(actual_attempt) + "/" + str(retries))
            match = self.screen.exists(Pattern(image_path).similar(actual_similarity), timeout)
            if match:
                self.last_match_region = (match.getX(), match.getY(), match.getW(), match.getH())
                if capture_last_match:
                    self.capture_error(debug_image_name, debug_image_path, capture_last_match)
                self.screen.click(match)
                if clear_before:
                    self.screen.type("a", KeyModifier.CTRL)  # Select all
                    self.screen.type(Key.BACKSPACE)          # Clear
                if(enter):
                    self.screen.type(text + Key.ENTER)
                else:
                    self.screen.type(text)
                print("[OK] Text written.")
                return True
            else:
                print("[WARNING] Image not found. Retrying...")

        print("[FAIL] Failed to write text.")
        return False
    
    def drag_and_drop(self, source_image_path, target_image_path, similarity=1.0, timeout=2, retries=6, similarity_reduction=0.1):
        """
        Performs a drag and drop from the source image to the target image.

        :param source_image_path: Path to the image to drag from.
        :param target_image_path: Path to the image to drop to.
        :param similarity: Starting similarity threshold.
        :param timeout: Time to wait per attempt.
        :param retries: Number of attempts before giving up.
        :param similarity_reduction: Amount to reduce similarity per attempt.
        :return: True if successful, False otherwise.
        """
        for attempt in range(retries):
            actual_similarity = similarity - (similarity_reduction * attempt)
            actual_attempt = attempt + 1
            print("Attempts " + str(actual_attempt) + "/" + str(retries))
            source_match = self.screen.exists(Pattern(source_image_path).similar(actual_similarity), timeout)
            target_match = self.screen.exists(Pattern(target_image_path).similar(actual_similarity), timeout)
            if source_match and target_match:
                self.screen.dragDrop(source_match, target_match)
                print("[OK] Drag and drop performed.")
                return True
            else:
                print("[WARNING] Source or target image not found. Retrying...")

        print("[FAIL] Failed to perform drag and drop.")    
        return False

    """
        Capture the current screen and save it to a file.

        :param filename: Name of the file to save the screenshot as.
        :param folder: Directory in which to save the screenshot.
        :return: File path if successful; None on failure.
    """
    def capture_error(self, filename, folder=".", capture_last_match= False):
        try:
            if not os.path.exists(folder):
                os.makedirs(folder)
            if capture_last_match and self.last_match_region:
                print("[INFO] Capturing last match region.")
                x, y, w, h = self.last_match_region
                reg = Region(int(x), int(y), int(w), int(h))
                filepath = self.screen.capture(reg).save(folder, filename)
            else:
                filepath = self.screen.capture().save(folder, filename)
            print("[CAPTURE] Saved screenshot: " + str(filepath))
            return filepath
        except Exception as e:
            print("[ERROR] Failed to save screenshot: " + str(e))
            return None
    
    