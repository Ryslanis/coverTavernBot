import config
from ui.emoji import *


SPOTIFY_MODE = False
SPOTIFY_PREVIEW_DURATION_SEC = 30

# these indicators make the bot continue the process
NEW_COVER_INDICATOR = "Ты добавил: "
NEW_COVER_INDICATOR_CHANNEL = '🎤: '
NEWBIE_INDICATOR = f'Новый пользователь, оцените его уровень в комментах!'
RATING_INDICATOR = '🎧: '
WHO_WANTS_INDICATOR = f'Сколько ты готов поставить?'
FAKE_INDICATOR = 'Fake: '

# admins indicators for inline query
USERS_ACTIONS_COMMAND = 'users'
# admin options
ADD_POINTS = 'addpoints'
ADMIN_OPTIONS = [USERS_ACTIONS_COMMAND]
# cover statuses
WANTING = 'wanting'
COVERING = 'covering'
RATING = 'rating'
FINISHED = 'finished'
WASTED = 'wasted'
FAKE = 'fake'

# main options
if config.ENVIRONMENT == 'development':
    SEC_WANTING = 1000  # 86400 * 3
    SEC_COVERING = SEC_WANTING  # 24 hours
    SEC_RATING = SEC_WANTING  # * 2
    MAX_COVER_PARTICIPANTS = 2
    MIN_COVER_PARTICIPANTS = 2

    MAX_COVERS_AT_ONCE = 20  # 2
    MAX_COVERS_AT_ONCE_PREMIUM = 4  # 4

    MIN_VOTED = 1
    MIN_VOTED_LEVEL = 1
    MIN_DURATION = 30
    MAX_DURATION = 70
elif config.ENVIRONMENT == 'production':
    SEC_WANTING = 86400*2
    SEC_COVERING = 86400  # 24 hours
    SEC_RATING = 86400  # * 2
    MAX_COVER_PARTICIPANTS = 2
    MIN_COVER_PARTICIPANTS = 2

    MAX_COVERS_AT_ONCE = 1  # 2
    MAX_COVERS_AT_ONCE_PREMIUM = 4  # 4

    MIN_VOTED = 5
    MIN_VOTED_LEVEL = 15
    MIN_DURATION = 30
    MAX_DURATION = 70

POINTS = [0 for _ in range(MAX_COVER_PARTICIPANTS)]
POINTS[0] = 2  # for a winner
MIN_POINTS = 50

DEFAULT_FAKE_POINTS = 1000
GIVE_POINTS = [1, 2, 5, 10, 25]

COST_PREMIUM = 25
COST_ADD_COVER = 20

EXP_NEWBIE = 100
EXP_CP = EXP_NEWBIE
EXP_COVER = 0
EXP_VOICE = 0
EXP_VOTE = 0

SPLITTER = ' — '
PARAMETER_SPLITTER = ': '

TOP = 10

NEWBIE = 'новички'
BOTTOM = 'нубы'
LOW = 'низкий'
MIDDLE = 'средний'
HIGH = 'любитель'
PRO = 'профи'
BAD = 'Не дотягивает до любителя'

LEVELS = [PRO, HIGH, BAD]

MY_PERCENTAGE = 0.11
WINNER_PERCENTAGE = 1 - MY_PERCENTAGE
LAST_VOICES = 3

STOP_WORDS = ['guitar', 'official', 'mashup', 'band', 'группа', 'табы', 'tutorial', 'фингерстайл', 'fingerstyle',
              'remix', 'ремикс', 'на гитаре', 'гитара']

MUST_WORDS = ['cover', 'кавер']

def geometric_progression(min_value, max_value, count):
    r = (max_value / min_value) ** (1 / (count - 1))
    result = [round(min_value * r ** i) for i in range(count)]
    for i in range(count - 1, 0, -1):
        if result[i] % 10 != 0:
            diff = 10 - (result[i] % 10)
            result[i] += diff
            result[i - 1] = round(result[i] / r)
    if result[0] % 10 != 0:
        result[0] = 10 * (result[0] // 10 + 1)
    return result


def get_level_upgrade_scheme(min_value, max_value):
    result = geometric_progression(max_value, 14, min_value)
    return result


LVL_UPGRADE_SCHEME = geometric_progression(5000, 100000, 7)
EXPERIENCE = geometric_progression(100, 2000, MAX_COVER_PARTICIPANTS if MAX_COVER_PARTICIPANTS > 1 else 2)
EXPERIENCE.reverse()

STANDART_ARTISTS_RU = [
    "Егор Крид",
    "Баста",
    "Тимати",
    "Мот",
    "Нюша",
    "Алексей Воробьев",
    "Сергей Лазарев",
    "Земфира",
    "Алла Пугачева",
    "Дима Билан",
    "Макс Барских",
    "Полина Гагарина",
    "Слава КПСС",
    "Сергей Шнуров",
    "Алексей Чумаков",
    "Артур Пирожков",
    "Иван Дорн",
    "Ленинград"
]

STANDARD_ARTISTS_UA = [
    "Океан Ельзи",
    "Скрябін",
    "Сергій Бабкін",
    "Время и Стекло",
    "Монатик",
    "Ольга Полякова",
    "Друга Ріка",
    "Тіна Кароль",
    "Джамала",
    "Наталка Карпа",
    "Тартак",
    "Потап і Настя",
    "Марія Яремчук",
    "ВВ",
    "НеАнгели",
    "Бумбокс",
    "Тік",
    "Ірина Білик",
    "Христина Соловій"
]

STANDARD_ARTISTS = STANDART_ARTISTS_RU + STANDARD_ARTISTS_UA

if __name__ == '__main__':
    print(LVL_UPGRADE_SCHEME)
    print(EXPERIENCE)


