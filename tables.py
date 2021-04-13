from random import choice
import requests
from bs4 import BeautifulSoup
import sqlite3 as sql

desktop_agents = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 '
    'Safari/602.2.14',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 '
    'Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 '
    'Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.4) Gecko/20100614 Ubuntu/10.04 (lucid) Firefox/3.6.4',
    'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.13) Gecko/20080311 Firefox/2.0.0.13',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.20) Gecko/20081217 Firefox/2.0.0.20',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.14) Gecko/2009082707 Firefox/3.0.14 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:49.0) Gecko/20100101 Firefox/49.0']


def GetRandomHeader():
    return {'User-Agent': choice(desktop_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}


URL = 'https://www.kinopoisk.ru/popular/'
HOST = 'https://www.kinopoisk.ru/film'


def GetHtml(url, params=None):
    r = requests.get(url, headers=GetRandomHeader(), params=params)
    return r


def GetPages(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('a', class_='paginator__page-number')
    if pagination:
        return int(pagination[-1].get_text())
    else:
        return 1


def GetContentF(html):
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('p', class_='styles_root__2lwUN'):
        item = soup.find('p', class_='styles_root__2lwUN').get_text()
        return item
    else:
        return "This is a serial"


def ParseFilm(url_):
    html = GetHtml(url_)
    if html.status_code == 200:
        print('good')
        w = GetContentF(html.text)
        return w
    else:
        print('Error', html.status_code)
        return ParseFilm(url_)


def GetContent(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='desktop-rating-selection-film-item__content-wrapper')
    names = []
    for item in items:
        rating_ = '0.0'
        if item.find('span', class_='rating__value rating__value_positive'):
            rating_ = item.find('span', class_='rating__value rating__value_positive').get_text()
        if item.find('span', class_='rating__value rating__value_neutral'):
            rating_ = item.find('span', class_='rating__value rating__value_neutral').get_text()
        if item.find('span', class_='rating__value rating__value_negative'):
            rating_ = item.find('span', class_='rating__value rating__value_negative').get_text()

        if rating_[-1] == '%':
            if len(rating_) == 2:
                rating_ = '0.' + rating_[0]
            else:
                rating_ = rating_[0] + '.' + rating_[1]
        film = ParseFilm(HOST + item.find('a', class_='selection-film-item-meta__link').get('href'))
        title = item.find('p', class_='selection-film-item-meta__name').get_text()
        title = title.replace(chr(39), ' ')
        types = item.find_all('span', class_='selection-film-item-meta__meta-additional-item')
        names.append(
            {
                'title': title,
                'link': HOST + item.find('a', class_='selection-film-item-meta__link').get('href'),
                'type': types[-1].get_text(),
                'r': rating_,
                'desc': film
            }
        )
    return names


def CreateTables():
    tables_list = ['test', 'comedy', 'horror', 'cartoon', 'action', 'drama', 'adventure', 'romance', 'fantasy', 'crime',
                   'detective', 'thriller', 'documentary']
    text1 = "CREATE TABLE IF NOT EXISTS `"
    text2 = "` (`name` STRING, `link` STRING, `type` STRING, `rating` STRING, `description` STRING)"

    for i in tables_list:
        table_ = sql.connect(i + '.db')
        with table_:
            cursor = table_.cursor()
            cursor.execute(text1 + i + text2)
            table_.commit()


tables = {'комедия': 'comedy',
          'мультфильм': 'cartoon',
          'ужасы': 'horror',
          'боевик': 'action',
          'драма': 'drama',
          'приключения': 'adventure',
          'мелодрама': 'romance',
          'фантастика': 'fantasy',
          'криминал': 'crime',
          'детектив': 'detective',
          'триллер': 'thriller',
          'документальный': 'documentary'}


def FillTables(items):
    for item in items:
        for i in tables:
            if item['type'].find(i) != -1:
                cursor = sql.connect(tables[i] + '.db').cursor()
                cursor.execute(
                    f"INSERT INTO `{tables[i]}` VALUES ('{item['title']}', '{item['link']}', '{item['type']}', '{item['r']}', '{item['desc']}')")
    for i in tables:
        table = sql.connect(tables[i] + '.db')
        table.commit()


def Parse():
    html = GetHtml(URL)
    if html.status_code == 200:
        print('good')
        pages_count = GetPages(html.text)
        pages = []
        for j in range(1, pages_count + 1):
            print(j)
            html = GetHtml(URL, params={'page': j})
            pages.extend(GetContent(html.text))
        SaveFile(pages)
        FillTables(pages)
    else:
        print('error')


con = sql.connect('test.db')
cur = con.cursor()


def SaveFile(items):
    for item in items:
        cur.execute(
            f"INSERT INTO `test` VALUES ('{item['title']}', '{item['link']}', '{item['type']}', '{item['r']}', "
            f"'{item['desc']}')")
    cur.execute("SELECT * FROM `test`")
    con.commit()
