from random import random
import sqlite3 as sql
import vk_api
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import json

con = sql.connect('test.db')
comedy = sql.connect('comedy.db')
horror = sql.connect('horror.db')
cartoon = sql.connect('cartoon.db')
action = sql.connect('action.db')
drama = sql.connect('drama.db')
adventure = sql.connect('adventure.db')
romance = sql.connect('romance.db')
fantasy = sql.connect('fantasy.db')
crime = sql.connect('crime.db')
detective = sql.connect('detective.db')
thriller = sql.connect('thriller.db')
documentary = sql.connect('documentary.db')

# create the key in your club in VK
vk_session = vk_api.VkApi(token="...")
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, "There is id of your club")

keyboard = {
    "one_time": False,
    "buttons": [
        [{"action": {"type": "text", "label": "документальный"},
          "color": "primary"
          },
         {"action": {"type": "text", "label": "комедия"},
          "color": "primary"
          },
         {"action": {"type": "text", "label": "мультик"},
          "color": "primary"
          },
         {"action": {"type": "text", "label": "ужасы"},
          "color": "primary"
          }],
        [
            {"action": {"type": "text", "payload": "{\"button\": \"2\"}", "label": "боевик"},
             "color": "negative"
             },
            {"action": {"type": "text", "payload": "{\"button\": \"3\"}", "label": "мелодрама"},
             "color": "negative"
             },
            {"action": {"type": "text", "payload": "{\"button\": \"3\"}", "label": "фантастика"},
             "color": "negative"
             },
            {"action": {"type": "text", "payload": "{\"button\": \"3\"}", "label": "преступления"},
             "color": "negative"
             }
        ],
        [{"action": {"type": "text", "payload": "{\"button\": \"3\"}", "label": "детектив"},
          "color": "positive"
          },
         {"action": {"type": "text", "payload": "{\"button\": \"4\"}", "label": "триллер"},
          "color": "positive"
          },
         {"action": {"type": "text", "payload": "{\"button\": \"4\"}", "label": "приключения"},
          "color": "positive"
          },
         {"action": {"type": "text", "payload": "{\"button\": \"4\"}", "label": "драма"},
          "color": "positive"
          },
         ],
        [
            {"action": {"type": "text", "payload": "{\"button\": \"4\"}", "label": "Help"},
             "color": "negative"
             },
            {"action": {"type": "text", "payload": "{\"button\": \"4\"}", "label": "Фильм"},
             "color": "positive"
             },
        ]
    ]
}

keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))

HELP_MESSAGE = """
Данный бот создан для того чтобы порекомендовать вам какой-нибудь фильм

Также вы получите описание этого фильма, если это фильм, а не сериал. 
"""

FILM_DESC_TEMPLATE = """
{}
{}
Жанры: {}
Рейтинг: {}
{}
"""

genres = {
    'фильм': 'test',
    'мультик': 'cartoon',
    'комедия': 'comedy',
    'ужасы': 'horror',
    'боевик': 'action',
    'драма': 'drama',
    'приключения': 'adventure',
    'мелодрама': 'romance',
    'фантастика': 'fantasy',
    'фэнтези': 'fantasy',
    'криминал': 'crime',
    'детектив': 'detective',
    'триллер': 'thriller',
    'документальный': 'documentary',
}

dbs = {rus: sql.connect(eng + '.db').cursor() for rus, eng in genres.items()}


def send_message(user_id, message):
    vk.messages.send(user_id=user_id, random_id=get_random_id(), message=message, keyboard=keyboard)


for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
        command = event.obj.text.lower()
        if command and command not in genres:
            send_message(event.obj.from_id, HELP_MESSAGE)
            continue
        conn = dbs[command]
        genre = genres[command]
        query = "SELECT * FROM `{}`".format(genre)
        conn.execute(query)
        films = conn.fetchall()
        i = films[int(random() * 10000 % (len(films) - 1))]
        send_message(event.obj.from_id,
                     FILM_DESC_TEMPLATE.format(str(i[0]), str(i[1]), str(i[2]), str(i[3]), str(i[4])))
