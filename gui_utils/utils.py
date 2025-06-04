import time
from typing import List, Dict

import keyboard
import pyautogui
import win32api
import win32con


class GUI:
    def __init__(self, recipes: List[Dict], recipe_name: str):
        self.recipe = [r for r in recipes if recipe_name == r['Рецепт']][0]
        self.materials_list = self.recipe['Материалы']

    def _gui_find_item(self, item_name: str):
        pyautogui.moveTo(650, 215, duration=0.25)
        pyautogui.click()
        pyautogui.moveTo(380, 215, duration=0.25)
        pyautogui.click()
        win32api.SendMessage(win32con.HWND_BROADCAST, win32con.WM_INPUTLANGCHANGEREQUEST, 0, 0x0419)
        keyboard.write(item_name)
        pyautogui.moveTo(1040, 215, duration=0.25)
        pyautogui.click()

    def _gui_buy_item(self, col: int):
        pyautogui.moveTo(600, 300, duration=0.25)
        pyautogui.click()
        pyautogui.click()
        pyautogui.moveTo(500, 470, duration=0.25)
        pyautogui.click()
        pyautogui.click()
        pyautogui.press('backspace')
        time.sleep(0.5)
        keyboard.write(str(col))
        pyautogui.moveTo(430, 660, duration=0.25)
        pyautogui.click()
        pyautogui.moveTo(500, 480, duration=0.25)
        pyautogui.click()
        pyautogui.moveTo(360, 270, duration=0.25)
        pyautogui.click()
        pyautogui.moveTo(650, 215, duration=0.25)
        pyautogui.click()
        pyautogui.moveTo(700, 215, duration=0.25)
        pyautogui.click()

    def buy_item(self, item: str, col: int):
        self._gui_find_item(item_name=item)
        self._gui_buy_item(col=col)
        time.sleep(1)

    def buy_recipe(self, col: int):
        for m in self.materials_list:
            self.buy_item(item=m['Название'], col=m['Количество'] * col)
            time.sleep(1)