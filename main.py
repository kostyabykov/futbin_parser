from bs4 import BeautifulSoup
from selenium import webdriver
import os
import time as t
from datetime import datetime
import undetected_chromedriver as uc
import gc
import pandas as pd
import psycopg2

#DB_URI = db_uri_code
#API_TOKEN = tg_api_bot

#CHAT_ID = tg_chat_id

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument('--load-images=false')

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

db_connection = psycopg2.connect(DB_URI, sslmode='require')
db_object = db_connection.cursor()


url_list = []
version_list = ['versus_fire', 'winter_wildcards', 'headliners_2', 'headliners', 'versus_ice', 'ucl_tott',
                'signature_signings', 'all_rttk','adidas','halloween', 'otw', 'toty_honourable', 'future_stars']
print(version_list)

for version in version_list:
    url = f"https://www.futbin.com/22/players?page=1&version={version}&sort=ps_price&order=desc"

    driver = uc.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
    driver.get(url)
    requiredHtml = driver.page_source
    driver.quit()
    soup = BeautifulSoup(requiredHtml, 'lxml')
    table = soup.find_all('tr')
    players = [row.get_attribute_list('data-url')[0] for row in table if row.has_attr('data-url')]
    for player in players:
        url_player = "https://www.futbin.com" + player
        url_list.append(url_player)
    if len(players) == 30:
        url = f"https://www.futbin.com/22/players?page=2&version={version}&sort=ps_price&order=desc"
        driver = uc.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
        driver.get(url)
        requiredHtml = driver.page_source
        driver.quit()
        soup = BeautifulSoup(requiredHtml, 'lxml')
        table = soup.find_all('tr')
        players = [row.get_attribute_list('data-url')[0] for row in table if row.has_attr('data-url')]
        for player in players:
            url_player = "https://www.futbin.com" + player
            url_list.append(url_player)
    print(f'{version} scanned')
    t.sleep(6)
print(f'URL_LIST LENGHT IS {len(url_list)}')
#players_data = pd.DataFrame(columns = ['time', 'name', 'rating', 'position', 'club', 'nation', 'league', 'skills', 'weak_f',
#                'att', 'deff', 'added', 'origin', 'b_type', 'day_of_week', 'time_delta', 'price'])

url_list_clear = [] # change
for i in range(len(url_list)):
    url = url_list[i]
    driver = uc.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
    driver.get(url)
    requiredHtml = driver.page_source
    driver.quit()
    soup = BeautifulSoup(requiredHtml, 'lxml')
    origin = soup.find_all("td", {'class': 'table-row-text'})[10].text.strip()
    price = int(soup.find('span', class_='price_big_right').text.replace(',', '').replace('\n', '').replace('-', '0'))
    if 'SBC' not in origin and 'Obj' not in origin:
        url_list_clear.append(url)
        if price != 0:
            rating = soup.find('div', {"class": "pcdisplay-rat"}).text.strip()
            position = soup.find('div', {"class": "pcdisplay-pos"}).text.strip()
            name = soup.find_all("td", {'class': 'table-row-text'})[0].text.strip()
            club = soup.find_all("td", {'class': 'table-row-text'})[1].text.strip()
            nation = soup.find_all("td", {'class': 'table-row-text'})[2].text.strip()
            league = soup.find_all("td", {'class': 'table-row-text'})[3].text.strip()
            skills = soup.find_all("td", {'class': 'table-row-text'})[4].text.strip()
            weak_f = soup.find_all("td", {'class': 'table-row-text'})[5].text.strip()
            att = soup.find_all("td", {'class': 'table-row-text'})[11].text.strip()
            deff = soup.find_all("td", {'class': 'table-row-text'})[12].text.strip()
            added = pd.to_datetime(soup.find_all("td", {'class': 'table-row-text'})[13].text.strip())
            origin = soup.find_all("td", {'class': 'table-row-text'})[10].text.strip()
            b_type = soup.find_all("td", {'class': 'table-row-text'})[16].text.strip()
            time = datetime.now()
            day_of_week = datetime.now().weekday()
            time_delta = time - added

            db_object.execute(
                'INSERT INTO players_df(time, name, rating, position, club, nation, league, skills, weak_f, att, deff, added, origin, b_type, day_of_week, time_delta, price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                (time, name, rating, position, club, nation, league, skills, weak_f, att, deff, added, origin, b_type,
                 day_of_week, time_delta, price))
            db_connection.commit()

            print(f'{i}) {name}')
t.sleep(8)


print(f'URL_LIST_CLEAR LENGHT: {len(url_list_clear)}')

while True:
    for i in range(len(url_list_clear)):
        url = url_list_clear[i]
        driver = uc.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
        driver.get(url)
        requiredHtml = driver.page_source
        driver.quit()
        soup = BeautifulSoup(requiredHtml, 'lxml')
        origin = soup.find_all("td", {'class': 'table-row-text'})[10].text.strip()
        price = int(soup.find('span', class_='price_big_right').text.replace(',', '').replace('\n', '').replace('-', '0'))
        if 'SBC' not in origin and 'Obj' not in origin and price!=0:
            rating = soup.find('div', {"class": "pcdisplay-rat"}).text.strip()
            position = soup.find('div', {"class": "pcdisplay-pos"}).text.strip()
            name = soup.find_all("td", {'class': 'table-row-text'})[0].text.strip()
            club = soup.find_all("td", {'class': 'table-row-text'})[1].text.strip()
            nation = soup.find_all("td", {'class': 'table-row-text'})[2].text.strip()
            league = soup.find_all("td", {'class': 'table-row-text'})[3].text.strip()
            skills = soup.find_all("td", {'class': 'table-row-text'})[4].text.strip()
            weak_f = soup.find_all("td", {'class': 'table-row-text'})[5].text.strip()
            att = soup.find_all("td", {'class': 'table-row-text'})[11].text.strip()
            deff = soup.find_all("td", {'class': 'table-row-text'})[12].text.strip()
            added = pd.to_datetime(soup.find_all("td", {'class': 'table-row-text'})[13].text.strip())
            origin = soup.find_all("td", {'class': 'table-row-text'})[10].text.strip()
            b_type = soup.find_all("td", {'class': 'table-row-text'})[16].text.strip()
            time = datetime.now()
            day_of_week = datetime.now().weekday()
            time_delta = time - added

            db_object.execute('INSERT INTO players_df(time, name, rating, position, club, nation, league, skills, weak_f, att, deff, added, origin, b_type, day_of_week, time_delta, price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (time, name, rating, position, club, nation, league, skills, weak_f, att, deff, added, origin, b_type, day_of_week, time_delta, price))
            db_connection.commit()

            print(f'{i}) {name}')
        else:
            print(f"{i} - {origin} - {price}")
    gc.collect
    t.sleep(8)
