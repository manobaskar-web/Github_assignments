import pyautogui
import time

#Mouse operation
pyautogui.moveTo(100, 100, duration=1)  # Move the mouse to (100, 100) over 1 second#
#Mouse click
pyautogui.click(100, 100)  # Click the mouse at (100, 100)  
#mouse right click
pyautogui.rightClick(100, 100)  # Right-click the mouse at (100, 100)
#mouse double click
pyautogui.doubleClick(100, 100)  # Double-click the mouse at (100, 100)                 
pyautogui.leftClick(100, 100)  # Left-click the mouse at (100, 100)
#Mouse drag
pyautogui.drag(100, 100, duration=1)  # Drag the mouse to (100, 100) over 1 second  
pyautogui.scroll(500)  # Scroll up 500  units
time.sleep(5)  # Wait for 5 seconds

pyautogui.scroll(-500)  # Scroll down 500 units 
