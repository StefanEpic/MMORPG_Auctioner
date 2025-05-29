import re
from typing import Dict

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from urllib.parse import unquote
from selenium.webdriver.common.by import By

PROXY = "192.168.17.89:3128"


def correct_item_name(item_name: str) -> str:
    item_name = re.sub(r'\(\d+\)', '', item_name[1:-1])
    return item_name.strip()


def create_items_price_dict(raw_text: str) -> Dict[str, int]:
    rows = raw_text.split('\n')
    items = dict()
    for r in rows[1:]:
        split_row = r.split(',')
        price = int(split_row[0])
        name = correct_item_name(",".join(split_row[1:-2]))
        items[name] = price
    return items


def get_driver(download_dir: str = 'temp') -> webdriver:
    options = webdriver.ChromeOptions()
    options.add_argument(f'--proxy-server={PROXY}')  # Опция настройки прокси сервера
    options.add_argument('--headless')  # Опция запуска браузера в фоновом режиме
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument('--disable-infobars')
    options.add_experimental_option('extensionLoadTimeout', 120000)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('prefs', {
        "download.default_directory": download_dir,  # Директория сохранения скаченных файлов
        "download.prompt_for_download": False,  # Отключение подтверждения скачивания
        "download.directory_upgrade": True,
    })
    return webdriver.Chrome(options=options, service=Service(executable_path='chromedriver.exe'))


def run(work_url: str):
    driver = get_driver()
    results = dict()
    try:
        driver.get(work_url)
        driver.set_window_size(1920, 1080)
        driver.fullscreen_window()

        table_rows = driver.find_element(By.ID, "main").find_element(By.CLASS_NAME,
                                                                     "listview-mode-default").find_elements(
            By.CLASS_NAME,
            'listview-row')
        for row in table_rows:
            td_list = row.find_elements(By.TAG_NAME, 'td')
            item_name = td_list[1].text
            quantity = td_list[0].text if td_list[0].text else "1"
            materials = dict()
            div_list = td_list[2].find_elements(By.TAG_NAME, 'div')
            for div in div_list:
                material_name = div.find_element(By.TAG_NAME, 'a').get_attribute('href')
                material_name = " ".join(unquote(material_name.split('/')[-1]).split('-')).capitalize()
                try:
                    material_col = div.find_element(By.TAG_NAME, 'span').text
                except:
                    material_col = "1"
                materials[material_name] = material_col
            r = dict()
            r['Количество'] = quantity
            r['Материалы'] = materials
            results[item_name] = r
        return results
    except Exception as e:
        print(e)
    finally:
        driver.delete_all_cookies()
        driver.close()
        driver.quit()
