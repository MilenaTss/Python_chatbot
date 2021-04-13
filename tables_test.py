import unittest
import sqlite3 as sql
from tables import GetRandomHeader
from tables import desktop_agents
from tables import GetHtml
from tables import GetPages
from tables import GetContent
from tables import ParseFilm
from tables import FillTables
from tables import SaveFile
from tables import Parse

com = sql.connect('comedy.db').cursor()
thr = sql.connect('thriller.db').cursor()
car = sql.connect('cartoon.db').cursor()
con = sql.connect('test.db')
cur = con.cursor()


class RandomHeadersTest(unittest.TestCase):
    def test_user(self):
        self.assertTrue(GetRandomHeader()['User-Agent'] in desktop_agents)

    def test_accept(self):
        self.assertEqual(GetRandomHeader()['Accept'],
                         'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')


class GetHtmlTest(unittest.TestCase):
    def test_status_code(self):
        self.assertEqual(GetHtml('https://www.kinopoisk.ru/series/685246/').status_code, 200)
        self.assertEqual(GetHtml('https://www.kinopoisk.ru/popular/').status_code, 200)
        self.assertEqual(GetHtml('https://www.kinopoisk.ru/film/1046486/').status_code, 200)
        self.assertEqual(GetHtml('https://www.kinopoisk.ru/film/film/1007761/').status_code, 200)

    def test_text(self):
        self.assertNotEqual(GetHtml('https://www.kinopoisk.ru/series/685246/'), "")
        self.assertNotEqual(GetHtml('https://www.kinopoisk.ru/popular/'), "")
        self.assertNotEqual(GetHtml('https://www.kinopoisk.ru/film/1046486/'), "")
        self.assertNotEqual(GetHtml('https://www.kinopoisk.ru/film/film/1007761/'), "")


class GetPagesTest(unittest.TestCase):
    def test_status_code(self):
        self.assertEqual(GetPages(GetHtml('https://www.kinopoisk.ru/popular/').text), 34)
        self.assertEqual(GetPages(GetHtml('https://www.kinopoisk.ru/lists/editorial/theme_school/').text), 1)


class ParseFilmTest(unittest.TestCase):
    def test_status_code(self):
        self.assertEqual(ParseFilm('https://www.kinopoisk.ru/series/685246/'), 'This is a serial')
        self.assertNotEqual(ParseFilm('https://www.kinopoisk.ru/film/film/1108494/'), 'This is a serial')


class GetContentTest(unittest.TestCase):
    def test_status_code(self):
        self.assertEqual(GetContent(GetHtml('https://www.kinopoisk.ru/popular/').text)[0]['title'], 'Рик и Морти')
        self.assertEqual(GetContent(GetHtml('https://www.kinopoisk.ru/popular/?page=5&tab=all').text)[11]['type'],
                         'мультфильм, ужасы')
        self.assertEqual(GetContent(GetHtml('https://www.kinopoisk.ru/popular/?page=7&tab=all').text)[3]['r'], '8.1')
        self.assertEqual(GetContent(GetHtml('https://www.kinopoisk.ru/popular/?page=7&tab=all').text)[3]['desc'],
                         'This is a serial')
        self.assertEqual(GetContent(GetHtml('https://www.kinopoisk.ru/popular/?page=7&tab=all').text)[28]['link'],
                         'https://www.kinopoisk.ru/film/film/762738/')


class SaveFileTest(unittest.TestCase):
    def test_status_code(self):
        FillTables(GetContent(GetHtml('https://www.kinopoisk.ru/popular/').text))
        com.execute("SELECT * FROM `comedy`")
        s = com.fetchall()
        i = s[0]
        f = i[0]
        self.assertEqual(f, 'Рик и Морти')
        thr.execute("SELECT * FROM `thriller`")
        s = thr.fetchall()
        i = s[2]
        self.assertEqual(i[1], 'https://www.kinopoisk.ru/film/film/1117735/')
        FillTables(GetContent(GetHtml('https://www.kinopoisk.ru/popular/?page=2&tab=all').text))
        car.execute("SELECT * FROM `cartoon`")
        s = car.fetchall()
        i = s[2]
        self.assertEqual(i[0], 'Вперёд')
        i = s[3]
        self.assertEqual(i[3], 6.5)
        i = s[4]
        self.assertEqual(i[4], 'This is a serial')
        com.execute("DELETE FROM `comedy`")
        com.execute("DELETE FROM `thriller`")
        com.execute("DELETE FROM `cartoon`")


class FillTablesTest(unittest.TestCase):
    def test_status_code(self):
        SaveFile(GetContent(GetHtml('https://www.kinopoisk.ru/popular/').text))
        cur.execute("SELECT * FROM `test`")
        s = cur.fetchall()
        i = s[0]
        f = i[0]
        self.assertEqual(f, 'Рик и Морти')
        i = s[3]
        self.assertEqual(i[1], 'https://www.kinopoisk.ru/film/film/1046206/')
        SaveFile(GetContent(GetHtml('https://www.kinopoisk.ru/popular/?page=2&tab=all').text))
        cur.execute("SELECT * FROM `test`")
        s = cur.fetchall()
        i = s[30]
        self.assertEqual(i[2], 'драма, комедия')
        i = s[35]
        self.assertEqual(i[3], 8)
        i = s[38]
        self.assertEqual(i[4], 'This is a serial')
        com.execute("DELETE FROM `test`")


class ParseTest(unittest.TestCase):
    def test_status_code(self):
        Parse()
        cur.execute("SELECT * FROM `test`")
        s = cur.fetchall()
        i = s[0]
        f = i[0]
        self.assertEqual(f, 'Рик и Морти')
        i = s[3]
        self.assertEqual(i[1], 'https://www.kinopoisk.ru/film/film/1046206/')
        i = s[30]
        self.assertEqual(i[2], 'драма, комедия')
        i = s[35]
        self.assertEqual(i[3], 8)
        i = s[38]
        self.assertEqual(i[4], 'This is a serial')


if __name__ == '__main__':
    unittest.main()
