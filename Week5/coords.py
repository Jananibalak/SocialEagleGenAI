# Source - https://stackoverflow.com/a/70948244
# Posted by Guilherme Matheus
# Retrieved 2026-02-19, License - CC BY-SA 4.0

import pyautogui
import time

time.sleep(5)
if pyautogui.locateOnScreen("search_icon.png", grayscale=True, confidence=0.8) != None:
    first_match=pyautogui.locateOnScreen("search_icon.png", grayscale=True, confidence=0.8)

center = pyautogui.center(first_match)
pyautogui.doubleClick(center.x//2, center.y//2)
pyautogui.doubleClick(center.x//2, center.y//2)
print(f"Clicking search icon at: {center}")