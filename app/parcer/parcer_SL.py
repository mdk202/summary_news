import requests
from bs4 import BeautifulSoup
import random
import re
from app.agents import USERAGENTS
from datetime import datetime


headers = {'Accept': '*/*',
           'User-Agent': f'{random.choice(USERAGENTS)}'}
start_url = 'https://www.securitylab.ru'
list_links_seclab = []


def parse_SL(page_counter=1):
    while True:
        url = start_url + f'/news/page1_{page_counter}.php'
        req = requests.get(url, headers)
        soup = BeautifulSoup(req.text, 'lxml')
        # Получаем все статьи на странице
        all_news = soup.find_all(class_='article-card inline-card')
        # Проходимся по каждой статье
        for item in all_news:
            all_news_dict = {}
            # Получаем время публикации и ссылку на статью
            item_href = item.get('href')
            item_date = item.find('time').text
            # Заносим в словарь данные о статье
            all_news_dict['date'] = item_date
            all_news_dict['url'] = start_url + f'{item_href}'
            # Добавляем статью в список
            list_links_seclab.append(all_news_dict)
        page_counter += 1
        # Продолжаем парсить статьи, пока не закончаться новости за текущий день
        for i in range(len(list_links_seclab)):
            if str(datetime.now().day) not in list_links_seclab[i]["date"]:
                del list_links_seclab[i:len(list_links_seclab)]
                return list_links_seclab


def parse_detail_SL(all_news):
    for index, news in enumerate(all_news):
        req = requests.get(news['url'], headers)
        src_1 = req.text
        soup = BeautifulSoup(src_1, 'lxml')
        project_data = soup.find('div', class_='articl-text')
        project_text = project_data.find_all('p')
        article_text = ''
        for item in project_text:
            article_text += item.text
        article_text = re.sub(r'\s+', ' ', article_text)
        all_news[index]['text'] = article_text
    print('Получены тексты всех статей с сайта SecurityLab\n')
    return all_news
