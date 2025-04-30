# -*- coding: utf-8 -*-
import os
from sikuli import Screen, Pattern, Region

# Imprimir la ruta actual
current_path = os.getcwd()
image_path = os.path.join(current_path, "imgs", "image.png")

screen = Screen()

# Click directly on the image
screen.click(image_path)

screen_width = screen.w
screen_height = screen.h
print("Screen dimensions: {}x{}".format(screen_width, screen_height))

# Create a region to search for the image
region = Region(400, 900, 350, 60)

# Save the region screenshot for debugging
region_screenshot_path = os.path.join(current_path, "region_screenshot.png")
screen.capture(region).save(current_path, "region_screenshot.png")
print("Region screenshot saved at: {}".format(region_screenshot_path))

# Adjust the precision of the image search
image = Pattern(image_path).similar(0.7)

# Search in the specified region for the image
# and click on it if found
if region.exists(image, 10):  # Search for 10 seconds
    region.click(image)
    print("Button found and clicked")
else:
    print("Button not found")
    # Save a screenshot of the region for debugging
    screen.capture(region).save(current_path, "debug_screenshot.png")
    print("Screenshot saved as debug_screenshot.png")
