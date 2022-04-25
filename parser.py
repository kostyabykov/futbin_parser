from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import os
import undetected_chromedriver as uc
import gc
import pandas as pd

#API_TOKEN = tg_api_token

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

data = pd.DataFrame(columns=['URL', 'old_price', 'SBC'])

url = "https://www.futbin.com/players?page=" + str(4) + "&version=non_icons&sort=ps_price&order=desc"
driver = uc.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
driver.get(url)
requiredHtml = driver.page_source
driver.quit()
soup = BeautifulSoup(requiredHtml, 'lxml')
table = soup.find_all('tr')
players = [row.get_attribute_list('data-url')[0] for row in table if row.has_attr('data-url')]
players = ["https://www.futbin.com" + player for player in players]
del soup
data['URL'] = players
data['old_price'] = 0
data['SBC'] = 0

def sendtext(message):
    url_tg = f'https://api.telegram.org/bot{API_TOKEN}/sendMessage?chat_id={CHAT_ID}&parse_mode=Markdown&text={message}'
    response = requests.get(url_tg)
    return response.json()


def emojji(income):
    import emoji
    if 2500<=income<5000:
        return(emoji.emojize(':fire: Name: '))
    if 5000<=income<10000:
        return(emoji.emojize(':fire::fire: Name: '))
    if income>=10000:
        return(emoji.emojize(':fire::fire::fire: Name: '))
    else:
        return ('Name: ')


def first_check(i):
    url = data['URL'][i]
    driver = uc.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    driver.quit()
    revision = soup.find_all("td", {'class': 'table-row-text'})[10].text
    current_price = int(soup.find('span', class_='price_big_right').text.replace(',', '').replace('\n', '').replace('-', '0'))
    data['old_price'][i] = current_price
    if 'SBC' in revision:
        data['SBC'][i] = 'True'
    else:
        data['SBC'][i] = 'False'
    print(i, url[url.find('/', 34)+1:], current_price, data['SBC'][i])

start = 0
step = 1
finish = len(data)
print('starting first check')
for i in range(start, finish, step):
    first_check(i)

print('DROP SBC CARDS')
data_ok = data[data['SBC'] == 'False'].reset_index(drop=True)

def second_check(i):
    url = data_ok['URL'][i]
    old_price = data_ok['old_price'][i]
    driver = uc.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    driver.quit()
    current_price = soup.find('span', class_='price_big_right').text
    del soup
    current_price = int(current_price.replace(',', '').replace('\n', '').replace('-', '0'))
    gc.collect()
    #print(f'{i}) {old_price[i]}, {current_price}\n')
    print(i)
    if 0.95 * old_price - current_price > 2000 and current_price != 0 and old_price != 0:
        income = int(0.95 * old_price - current_price)
        name = url[url.find('/', 34)+1:]
        sendtext(f'{emojji(income)}{name}\n Income: {income}\n'
                f'New price: {current_price}\nOld price: {old_price}\nURL: {url}')
    data_ok['old_price'][i] = current_price

print('starting second check')
while True:
    start = 0
    step = 1
    finish = len(data_ok)
    for i in range(start, finish, step):
        second_check(i)

