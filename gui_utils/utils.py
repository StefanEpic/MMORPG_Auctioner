import keyboard
import pyautogui


def find_item(item_name: str):
    pyautogui.moveTo(700, 300, duration=0.25)
    pyautogui.click()
    keyboard.write(item_name)
