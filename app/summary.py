from app.agents import STOPWORDS
from itertools import combinations
import networkx as nx
import numpy as np
import razdel
import pymorphy2
import re
import json


def unique_words_similarity(sentence1, sentence2):
    """
    Функция подсчёта близости предложений на основе пересечения слов
    """
    sentence1 = set(sentence1)
    sentence2 = set(sentence2)
    if not len(sentence1) or not len(sentence2):
        return 0.0
    return len(sentence1.intersection(sentence2)) / (np.log10(len(sentence1)) + np.log10(len(sentence2)))


def tokenization_sentences(text):
    """
    Функция для очистки (стоп-слова, знаки препинания) и токенизации предложений
    """
    stopword = STOPWORDS
    text = set(re.sub(r'[^\w\s]', '', text).split())
    for word in stopword:
        if word in text:
            text.remove(word)
    new_text = list(text)
    return new_text


def gen_text_rank_summary(text, calc_similarity=unique_words_similarity, summary_part=0.5):
    """
    Составление summary с помощью TextRank
    """
    # Разбиваем текст на предложения
    sentences = [sentence.text for sentence in razdel.sentenize(text)]
    n_sentences = len(sentences)

    # Токенизируем предложения (получаем список со списками токенизированных преложений)
    sentences_words = [tokenization_sentences(sentence.text.lower()) for sentence in razdel.sentenize(text)]

    # Лемматизируем слова
    morph = pymorphy2.MorphAnalyzer()
    sentences_words = [[morph.parse(word)[0].normal_form for word in words] for words in sentences_words]

    # Находим все возможные комбинации пар предложений
    pairs = combinations(range(n_sentences), 2)
    # Для каждой пары предложений считаем близость (получачем кортежи
    # с номерами преложений и значением близости (0, 1, 0,589))
    scores = [(i, j, calc_similarity(sentences_words[i], sentences_words[j])) for i, j in pairs]

    # Строим граф с рёбрами, равными близости между предложениями
    g = nx.Graph()
    g.add_weighted_edges_from(scores)

    # Считаем PageRank
    pr = nx.pagerank(g)
    result = [(i, pr[i], s) for i, s in enumerate(sentences) if i in pr]
    result.sort(key=lambda x: x[1], reverse=True)

    # Выбираем топ предложений
    n_summary_sentences = max(int(n_sentences * summary_part), 1)
    result = result[:n_summary_sentences]

    # Восстанавливаем оригинальный их порядок
    result.sort(key=lambda x: x[0])

    # Восстанавливаем текст выжимки
    predicted_summary = " ".join([sentence for i, proba, sentence in result])
    return predicted_summary


def calc_text_rank_score(records, site, calc_similarity=unique_words_similarity, summary_part=0.1):
    for index, news in enumerate(records):
        predicted_summary = gen_text_rank_summary(news['text'], calc_similarity, summary_part)
        # predictions.append(predicted_summary)
        records[index]['summary'] = predicted_summary
    records.reverse()
    if site == 'CNews':
        with open('app/news/result_CNews.json', 'w', encoding='utf-8') as fp:
            json.dump(records, fp, ensure_ascii=False)
    elif site == '3DNews':
        with open('app/news/result_3DNews.json', 'w', encoding='utf-8') as fp:
            json.dump(records, fp, ensure_ascii=False)
    elif site == 'SecurityLab':
        with open('app/news/result_SecurityLab.json', 'w', encoding='utf-8') as fp:
            json.dump(records, fp, ensure_ascii=False)
    return records
