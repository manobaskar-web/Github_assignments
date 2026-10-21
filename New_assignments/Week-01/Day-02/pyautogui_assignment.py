import pyautogui
import time
from datetime import datetime
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5
print ("Step-1- open the chrome browser  ")
pyautogui.hotkey('win', 'r')  # Open the Run dialog
time.sleep(1)
pyautogui.write('chrome')  # Type 'chrome'
time.sleep(1)
pyautogui.press('select')  # Press Enter to open Chrome  
time.sleep(3)  # 
pyautogui.press('enter' )  # Press Enter to open Chrome
print("Step-2- mano baskar chrome browser opened successfully")
pyautogui.dragTo(934, 400, duration=1)  # Move the mouse to the Chrome window
pyautogui.doubleClick(934, 400)  # Click  on the Chrome window to focus it
time.sleep(1)
pyautogui.hotkey('ctrl', 't')  # Open a new tab
pyautogui.write('today weather, gold rate, today headline all in one')  # Type the URL
pyautogui.press('enter')  # Press Enter to navigate to the URL
time.sleep(5)  # Wait for the page to load
print("Step-3- copy the full data from the page") 
pyautogui.moveTo(190, 400, duration=5,)  # Move the mouse to the top-left corner of the page     
pyautogui.dragTo(1000, 430, duration=5,button='left')  # Move the mouse to the top-left corner of the page 
pyautogui.hotkey('ctrl', 'c')  # Copy the selected text
time.sleep(1)
print("Step-4- open the excel and paste the data")
pyautogui.hotkey('win', 'r')  # Open the Run dialog
pyautogui.write('excel')  # Type 'excel'
pyautogui.press('enter')  # Press Enter to open Excel
time.sleep(7)  # Wait for Excel to open
pyautogui.press('enter')  # Press Enter to open a new workbook
time.sleep(3)  # Wait for the new workbook to open  

print("Step-5- enter heading the data in excel")

# -----------------------------
# STEP 5: Enter headings
# -----------------------------
pyautogui.write("Date and Time")
pyautogui.press("tab")

pyautogui.write("Weather")
pyautogui.press("tab")

pyautogui.write("Comment")
pyautogui.press("enter")

# -----------------------------
# STEP 6: Enter today's data
# -----------------------------
now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

pyautogui.write(now)
pyautogui.press("tab")

# Paste copied weather value
pyautogui.hotkey("ctrl", "v")
pyautogui.press("tab")

pyautogui.write("Good for outdoor activities")

# -----------------------------
# STEP 7: Save Excel file
# -----------------------------
today = datetime.now().strftime("%d-%m-%Y")
filename = f"daily_report_{today}.xlsx"

pyautogui.hotkey("ctrl", "shift", "s")
time.sleep(3)

pyautogui.write(filename)
time.sleep(1)

pyautogui.press("enter")
time.sleep(5)

# -----------------------------
# STEP 8: Take screenshot
# -----------------------------
screenshot_name = f"daily_report_{today}.png"

pyautogui.screenshot(screenshot_name)

print("Automation completed successfully.")
print("Excel file:", filename)
print("Screenshot:", screenshot_name)







