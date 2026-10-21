import pyautogui
import pyscreeze
import time
#keyboard operation
pyautogui.typewrite("Hello, World!")  # Type "Hello, World!"
#hotkey operation
pyautogui.hotkey('ctrl', 'c')  # Press Ctrl+C   
#single key press   
pyautogui.press('enter')  # Press the Enter key 
#key down and key up
pyautogui.keyDown('shift')  # Hold down the Shift key
pyautogui.keyUp('shift')  # Release the Shift key       

#pyautogui.FAILSAFE = True

#screenshot operation
screenshot = pyautogui.screenshot()  # Take a screenshot    
screenshot.save("screenshot.png")  # Save the screenshot as "screenshot.png"                
