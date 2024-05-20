import requests
from bs4 import BeautifulSoup
import random
import re
from app.agents import USERAGENTS


headers = {'Accept': '*/*',
           'User-Agent': f'{random.choice(USERAGENTS)}'}
start_url = 'https://www.cnews.ru/archive/type_top_lenta_articles/page_'


def parse_CN(page_counter=1):
    list_links_cnews = []
    while True:
        url = start_url + f'{page_counter}'
        req = requests.get(url, headers)
        soup = BeautifulSoup(req.text, 'lxml')
        # Получаем все статьи на странице
        all_news = soup.find_all(class_='allnews_item')
        # Проходимся по каждой статье
        for item in all_news:
            all_news_dict = {}
            # Получаем время публикации и ссылку на статью
            item_href = item.find('a').get('href')
            item_date = item.find('div', class_='ani-date').text.replace("\n", "")
            # Заносим в словарь данные о статье
            all_news_dict['date'] = item_date
            all_news_dict['url'] = item_href
            # Добавляем статью в список
            list_links_cnews.append(all_news_dict)
        page_counter += 1
        # Продолжаем парсить статьи, по не закончаться новости за текущий день
        for i in range(len(list_links_cnews)):
            if '.' in list_links_cnews[i]["date"] or 'Вчера' in list_links_cnews[i]["date"]:
                del list_links_cnews[i:len(list_links_cnews)]
                return list_links_cnews


def parse_detail_CN(all_news):
    for index, news in enumerate(all_news):
        req = requests.get(news['url'], headers)
        src_1 = req.text
        soup = BeautifulSoup(src_1, 'lxml')
        project_data = soup.find('article', class_='news_container')
        project_text = project_data.find_all('p')
        article_text = ''
        for item in project_text:
            article_text += item.text
        article_text = re.sub(r'\s+', ' ', article_text)
        all_news[index]['text'] = article_text
    print('Получены тексты всех статей с сайта CNews\n')
    return all_news
