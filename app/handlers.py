from aiogram import Router, F
from aiogram.filters.command import CommandStart
from aiogram.types import Message, CallbackQuery
from asyncio import sleep
import json
from itertools import chain

import app.keyboards as kb
from app.parcer.parcer_CN import parse_CN, parse_detail_CN
from app.parcer.parcer_SL import parse_SL, parse_detail_SL
from app.parcer.parcer_3d import parse_3d, parse_detail_3d
from app.summary import calc_text_rank_score

router = Router()
site = ''


@router.message(CommandStart())
async def start(message: Message):
    await message.answer('Привет!')
    await message.answer('Получаю новости')
    await sleep(15)

    # all_news_CN = parse_detail_CN(parse_CN())
    # calc_text_rank_score(all_news_CN, 'CNews')
    #
    # all_news_3D = parse_detail_3d(parse_3d())
    # calc_text_rank_score(all_news_3D, '3DNews')
    #
    # all_news_SL = parse_detail_SL(parse_SL())
    # calc_text_rank_score(all_news_SL, 'SecurityLab')

    await message.answer('Новости загружены', reply_markup=kb.main)


@router.message(F.text == 'Новости с сайта CNews')
async def quantity_CN(message: Message):
    global site
    site = 'CNews'
    await message.answer('Выберите количество новостей', reply_markup=kb.quantity)


@router.message(F.text == 'Новости с сайта 3DNews')
async def quantity_3D(message: Message):
    global site
    site = '3DNews'
    await message.answer(f'Выберите количество новостей', reply_markup=kb.quantity)


@router.message(F.text == 'Новости с сайта SecurityLab')
async def quantity_SL(message: Message):
    global site
    site = 'SecurityLab'
    await message.answer('Выберите количество новостей', reply_markup=kb.quantity)


@router.message(F.text == 'Все новости')
async def all_news(message: Message):
    for name_site in ['3DNews', 'SecurityLab', 'CNews']:
        with open(f'app/news/result_{name_site}.json', 'r', encoding='utf-8') as fp:
            news_CN = json.load(fp)
            if len(news_CN) > 0:
                for val in news_CN:
                    await message.answer(f'{val["summary"]}\n\nИсточник: {val["url"]}',
                                         disable_web_page_preview=True)
    await message.answer('Все новости на данный момент за текущий день')


@router.callback_query(F.data == 'all_news')
async def all_news_site(callback: CallbackQuery):
    global site
    with open(f'app/news/result_{site}.json', 'r', encoding='utf-8') as fp:
        news_CN = json.load(fp)
        if len(news_CN) > 0:
            for val in news_CN:
                await callback.message.answer(f'{val["summary"]}\n\nИсточник: {val["url"]}',
                                              disable_web_page_preview=True)
            await callback.answer()
            await callback.message.answer(f'Все новости с сайта {site}')
        else:
            await callback.answer()
            await callback.message.answer(f'На данный момент на сайте {site} нет новостей за текущий день')


@router.callback_query(F.data == 'last_five_news')
async def five_news(callback: CallbackQuery):
    global site
    with open(f'app/news/result_{site}.json', 'r', encoding='utf-8') as fp:
        news_CN = json.load(fp)
        if len(news_CN) > 0:
            for val in news_CN[-5:]:
                await callback.message.answer(f'{val["summary"]}\n\nИсточник: {val["url"]}',
                                              disable_web_page_preview=True)
            await callback.answer()
            await callback.message.answer(f'Последние 5 новостей с сайта {site}')
        else:
            await callback.answer()
            await callback.message.answer(f'На данный момент на сайте {site} нет новостей за текущий день')


@router.callback_query(F.data == 'fresh_news')
async def fresh_news(callback: CallbackQuery):
    global site
    list_new_news = []
    await callback.message.answer('Ищу свежие новости')
    with open(f'app/news/result_{site}.json', encoding='utf-8') as fp:
        old_news = json.load(fp)
        links = [parse_detail_3d(parse_3d()) if site == '3DNews' else parse_detail_CN(parse_CN()) if site == 'CNews' else parse_detail_SL(parse_SL())]
        new_news = calc_text_rank_score(list(chain.from_iterable(links)), 'None')
        for news in new_news[::-1]:
            if news not in old_news:
                list_new_news.append(news)
            else:
                break
    if len(list_new_news) > 0:
        with open(f'app/news/result_{site}.json', 'w', encoding='utf-8') as fp1:
            json.dump(new_news, fp1, ensure_ascii=False)
        for val in list_new_news:
            await callback.message.answer(f'{val["summary"]}\n\nИсточник: {val["url"]}',
                                          disable_web_page_preview=True)
        await callback.answer()
        await callback.message.answer(f'Все свежие новости с сайта {site}')
    else:
        await callback.answer()
        await callback.message.answer(f'На данный момент на сайте {site} нет свежих новостей')
