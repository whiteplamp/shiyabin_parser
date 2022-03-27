import json

from selenium import webdriver
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

# todo: Изменить названия файлов для удобного чтения из бота
# todo: Задеплоить парсер на сервер
# todo: Переписать бота под новый конфиг данных

URL = 'https://mobifitness.ru/schedule-widget/?code=759037&' \
      'type=schedule&club=0&host=mobifitness.ru&version=v6&parent=#/schedule'


def get_source(url):
    path = 'source/chromedriver.exe'
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(path)

    try:
        driver.get(url)
        time.sleep(5)
        for i in range(6):
            print_btn = driver.find_element(By.CLASS_NAME, "mf-widget-print-button")
            print_btn.click()
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(4)
            with open(f"source/html/index{i}.html", mode='w', encoding='utf8') as file:
                file.write(driver.page_source)
            driver.close()
            time.sleep(5)
            if i < 5:
                driver.switch_to.window(driver.window_handles[0])
                next_btn = driver.find_element(By.CLASS_NAME, "fa-chevron-right")
                next_btn.click()
                time.sleep(5)

    except Exception as e:
        print(e)

    finally:
        driver.quit()


def parse_lxml(path):
    with open(file=path, encoding='utf8') as file:
        src = file.read()

    soup = BeautifulSoup(src)
    table = soup.find('table')
    data_json_months = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    data_json = {"Monday": [],
                 "Tuesday": [],
                 "Wednesday": [],
                 "Thursday": [],
                 "Friday": [],
                 "Saturday": [],
                 "Sunday": []
                 }

    for i in range(7):
        data = table.find_all('tr')[-1].find_all('td', class_="fitness-widget-cell-bg")[i]. \
            find_all('div', class_='fitness-widget-cell')
        for element in data:
            title = \
                element.find("div", class_="fitness-widget-cell-title").get_text().split('\n            ')[-2].split(
                    '                        ')[-1]
            direction = ''
            if "цигун и тайцзи" in title.lower() or "тайцзи: кунг-фу" in title.lower() \
                    or "цигун и тайцзицюань" in title.lower():
                direction = "Цигун и тайцзицюань"
            elif "Shaolin XinYiBa" in title or "цигун-комплекс" in title.lower():
                direction = 'Кунг-фу и Shaolin XinYiBa «Внутренняя сила»'
            elif "оздоровительное кунг-фу с мечом дао" in title.lower() or "долголетие" in title.lower() \
                    or "занятия по традиционному китайскому танцу" in title.lower() \
                    or "здоровья" in title.lower() or "оздоровительная гимнастика" in title.lower() \
                    or "здоровье" in title.lower():
                direction = "Дополнительные занятия"
            elif "для детей" in title.lower() or "панды" in title.lower() or "кунг-фу: фехтование" in title.lower() \
                    or "бурые медведи" in title.lower() or "драконы" in title.lower() or "тигры" in title.lower():
                direction = "Детские занятия"
            elif "онлайн" in title.lower():
                direction = "Онлайн занятия"
            elif "кунг-фу" in title.lower():
                direction = "Современное кунг-фу"
            elif "индивидуальное занятие" in title.lower():
                direction = "Персональные занятия"
            else:
                direction = "Другое"

            data_json[data_json_months[i]].append(
                {"title":
                    element.find("div", class_="fitness-widget-cell-title").get_text().split('\n            ')[-2].
                    split('                        ')[-1],
                 "teacher":
                     element.find("div", class_="fitness-widget-cell-train").get_text().split('\n            ')[-1].
                     split("                                            ")[-1].split("\n")[0],
                 "starts": element.find("div", class_="fitness-widget-cell-time").get_text().split('\n    ')[-2].
                     split('            ')[-1].split(' - ')[0],
                 "ends": element.find("div", class_="fitness-widget-cell-time").get_text().split('\n    ')[-2].
                     split('            ')[-1].split(' - ')[1],
                 "direction": direction,
                 "description": element.find("div", class_="fitness-widget-cell-descr").get_text().
                     split("\n                    ")[-1].split("                            ")[0]
                 }
            )

    return data_json


def main():
    get_source(URL)
    for i in range(6):
        with open(f"source/json/schedule{i}.json", 'w', encoding='utf8') as file:
            json.dump(parse_lxml(f"source/html/index{i}.html"), file, indent=4)


if __name__ == '__main__':
    main()
