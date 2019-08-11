import urllib.request
import requests
import re
from transliterate import translit
import pandas as pd
from bs4 import BeautifulSoup
import datetime
import argparse


def life_news_collect(n, site='https://life.ru/'):
    """Скачивает главную страницу life.ru, ищет новости"""

    page = urllib.request.urlopen(site)
    text = page.read().decode('Utf-8')
    reg_news = re.compile('<div class="news-feed-container">.*?</div>',
                          flags=re.DOTALL)
    text = reg_news.findall(text)[0]
    reg_articles = re.compile('https://life.ru/\d{6,8}', re.DOTALL)
    articles = reg_articles.findall(text)
    articles = articles[::2][:n]
    return articles


def life_visit_articles(articles, name):
    """
    Посещает страницы life.ru и выкачивает информацию.
    Возвращает датафрейм pandas из следующих списков:
    Заголовок(name_z), статья(name_s), дата, источник(life.ru/), ссылка(article),
    название, тип новости, тип манипуляции(''), заголовок(название), пояснение, разметчик (NAME)
    """

    items = []
    for article in articles:
        page = requests.get(article)
        text = page.text

        source = 'https://life.ru/'
        href = article
        manipulation = ''
        reg_date = re.compile('datePublished" content=".*?T', flags=re.DOTALL)
        date = reg_date.findall(text)[0][24:-1]
        date = '{}.{}.{}'.format(date[-2:], date[5:7], date[:4])  # Переводим в формат день.месяц.год
        # date = f'{date[-2:]}.{date[5:7]}.{date[:4}'
        reg_title = re.compile('<title>.*?- «Life.ru»')
        title = reg_title.findall(text)[0][7:-12] # Аналогично с датой.
        reg_category = re.compile('<meta name="mediator_theme".*?>')
        category = reg_category.findall(text)[0][37:-2]
        name_z = translit(title, 'ru', reversed=True)[:9] + translit(title, 'ru', reversed=True)[12:15] + '_z'
        name_s = translit(title, 'ru', reversed=True)[:9] + translit(title, 'ru', reversed=True)[12:15] + '_s'
        item = [name_z, name_s, date, source, href, title, category,
                manipulation, title, article, name]
        items.append(item)

        # with open('{}.txt'.format(name_z), 'w', encoding='utf-8') as f:
        # f.write(title)

        page_content = BeautifulSoup(page.content, "html.parser")
        try:
            text_article = page_content.find_all(class_='longread-content')[0]
        except:
            text_article = page_content.find_all(class_='content-note js-mediator-article')[0]
        text_article = re.sub('<.*?>', '', str(text_article), flags=re.DOTALL)
        text_article = re.sub("\(function.*?yandexZenAsyncCallbacks'\);", '', text_article, flags=re.DOTALL)
        text_article = re.sub('\s{2,}', '\n', text_article)
        # with open('{}.txt'.format(name_s), 'w', encoding='utf-8') as f:
        # f.write(text_article)

        with open('life_lengths.txt', 'a', encoding='utf-8') as f:
            f.write(str(len(text_article)) + ' ')
    return pd.DataFrame(items)


def provlad_news_collect(n, site="https://provladimir.ru/"):
    """Собирает ссылки на новости с сайта газеты ПРОВЛАДИМИР"""
    page = requests.get(site)
    text = page.text

    reg_news = re.compile('<li class="post-item.*?" class="post-thumb"', flags=re.DOTALL)
    text = ''.join(reg_news.findall(text))
    reg_article = re.compile('https://provladimir.ru/.*?/"', flags=re.DOTALL)
    articles = reg_article.findall(text)
    articles = [article[:-1] for article in articles][:n]
    return articles


def provlad_visit_articles(articles, name):
    """
    Посещает страницы provladimir.ru и выкачивает информацию.
    Возвращает датафрейм pandas из следующих списков:
    Заголовок(name_z), статья(name_s), дата, источник(life.ru/), ссылка(article), название, тип новости, тип манипуляции(''), заголовок(название), пояснение, разметчик (NAME)
    """
    items = []
    for article in articles:
        page = requests.get(article)
        text = page.text

        name_z = article[-10:-1] + '_z'
        name_s = article[-10:-1] + '_s'
        date_reg = re.compile('\d{2}\.\d{2}\.\d{4}', flags=re.DOTALL)
        date = date_reg.findall(text)[0]
        source = "https://provladimir.ru/"
        reg_title = re.compile('<title>.*?</title>', flags=re.DOTALL)
        title = reg_title.findall(text)[0][7:-28]  # Костыль
        reg_category = re.compile('<meta property="article:tag" content=".*?" />', re.DOTALL)
        category = reg_category.findall(text)[-1][38:-4]
        item = [name_z, name_s, date, source,
                article, title, category,
                '', title, article, name]
        items.append(item)
        # with open('{}.txt'.format(name_z), 'w', encoding='utf-8') as f:
        # f.write(title)

        page_content = BeautifulSoup(page.content, "html.parser")
        text_article = page_content.find_all(class_='entry-content entry clearfix')[0]
        text_article = re.sub('<.*?>', '', str(text_article), flags=re.DOTALL)
        text_article = re.sub('\s{2,}', '\n', text_article)
        # with open('{}.txt'.format(name_s), 'w', encoding='utf-8') as f:
        # f.write(text_article)

        with open('provlad_lengths.txt', 'a', encoding='utf-8') as f:
            f.write(str(len(text_article)) + ' ')
    return pd.DataFrame(items)


def rbk_collect(n, site="https://www.rbc.ru/"):
    """Собирает ссылки на новости с сайта газеты РБК"""
    page = requests.get(site)
    text = page.text

    reg_news = re.compile('<div class="main__feed js-main-reload-item".*?</div>', flags=re.DOTALL)
    text = ''.join(reg_news.findall(text))
    articles_reg = re.compile('<a href=".*?"', flags=re.DOTALL)
    articles = ''.join(articles_reg.findall(text))
    articles_reg = re.compile('https://.*?_main', flags=re.DOTALL)
    articles = articles_reg.findall(articles)[:n]
    return articles


def rbk_visit_articles(articles, name):
    """
    Посещает страницы rbc.ru и выкачивает информацию.
    Возвращает датафрейм pandas из следующих списков:
    Заголовок(name_z), статья(name_s), дата, источник(life.ru/), ссылка(article), название, тип новости, тип манипуляции(''), заголовок(название), пояснение, разметчик (NAME)
    """
    items = []
    for article in articles:
        page = requests.get(article)
        text = page.text

        date_reg = re.compile('<span class="article__header__date".*?</span>', flags=re.DOTALL)
        date = date_reg.findall(text)[0]
        date = re.search('\d{4}-\d{2}-\d{2}', date, flags=re.DOTALL)[0]
        date = '{}.{}.{}'.format(date[-2:], date[5:7], date[:4])  # Переводим в формат день.месяц.год
        source = "https://www.rbc.ru/"

        reg_title = re.compile('<title>.*?</title>', flags=re.DOTALL)
        title = reg_title.findall(text)[0] # Костыль

        reg_category = re.compile(':: .*? ::', re.DOTALL)
        category = reg_category.findall(title)[0][3:-3]
        title = re.search('.*? ::', title)[0][7:-3]
        name_z = translit(title.replace(' ', ''), 'ru', reversed=True)[:9] + '_z'
        name_s = translit(title.replace(' ', ''), 'ru', reversed=True)[:9] + '_s'
        item = [name_z, name_s, date, source, article, title, category, '', title, article, name]
        items.append(item)

        # with open('{}.txt'.format(name_z), 'w', encoding='utf-8') as f:
        # f.write(title)

        page_content = BeautifulSoup(page.content, "html.parser")
        text_article = page_content.find_all(class_='article__text')
        text_article = re.sub("<a class=.*?</a>", '', str(text_article), flags=re.DOTALL)
        reg_text = re.compile('<p>.*?</p>', re.DOTALL)
        text_article = ''.join(reg_text.findall(str(text_article)))
        text_article = re.sub('<.*?>', '', str(text_article), flags=re.DOTALL)
        text_article = re.sub('\s{2,}', '\n', text_article)
        # with open('{}.txt'.format(name_s), 'w', encoding='utf-8') as f:
        # f.write(text_article)

        with open('rbk_lengths.txt', 'a', encoding='utf-8') as f:
            f.write(str(len(text_article)) + ' ')
    return pd.DataFrame(items)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parser Params')
    parser.add_argument(type=str, help='Who writes the data', dest='NAME')
    parser.add_argument(type=int, help='How many articles from each site is needed', dest="N")
    args = parser.parse_args()
    NAME = args.NAME
    N = args.N

    now = datetime.datetime.now()
    # os.mkdir("{}.{}".format(now.day, now.month))
    # os.chdir("{}.{}".format(now.day, now.month))

    life_articles = life_news_collect(n=N)
    life_items = life_visit_articles(life_articles, name=NAME)
    provlad_articles = provlad_news_collect(n=N)
    provlad_items = provlad_visit_articles(provlad_articles, name=NAME)
    rbk_articles = rbk_collect(n=N)
    rbk_items = rbk_visit_articles(rbk_articles, name=NAME)

    df = pd.concat([life_items, provlad_items, rbk_items])
    df.to_excel("Output.xlsx")
