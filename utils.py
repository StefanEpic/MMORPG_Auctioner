from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from urllib.parse import unquote
from selenium.webdriver.common.by import By

PROXY = "192.168.17.89:3128"


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
            materials_hrefs = [i.get_attribute('href') for i in td_list[2].find_elements(By.TAG_NAME, 'a')]
            materials_names = [" ".join(unquote(i.split('/')[-1]).split('-')).capitalize() for i in materials_hrefs]
            materials_col = [i.text for i in td_list[2].find_elements(By.TAG_NAME, 'span')]
            if not materials_col:
                materials_col = ["1" for _ in range(len(materials_names))]
            materials = dict()
            for i in zip(materials_names, materials_col):
                materials[i[0]] = i[1]

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
