import config
import settings
from settings import *
from ui.emoji import *

ERROR_NOT_REGISTERED = f"{ERROR} Пиши @{config.BOT_NAME}",
ERROR_ALREADY_PARTICIPANT = f"{ERROR} Ты уже участвуешь"
ERROR_ALREADY_RECORDED = f"{ERROR} Ты уже записал кавер на %s"
ERROR_MUST_CP = f'{ERROR} Ты на контрольной точке!'
ERROR_NOT_EVALUATED_CP = f'{ERROR} Подожди пока все оценят твой последний кавер.'
ERROR_LVL_DIFFERENCE = f"{ERROR} Твой уровень %d не соответсвует уровню участников кавера %s"
ERROR_NO_POINTS = f'{ERROR} Недостаточно очков.'
ERROR_MAX_PARTICIPANTS = f'{ERROR} На этот кавер уже согласились {MAX_COVER_PARTICIPANTS} человек'
ERROR_MIN_PARTICIPANTS = f'{ERROR} На этот кавер уже согласились {MAX_COVER_PARTICIPANTS} человек'
ERROR_TOO_MANY_COVERS = f'{ERROR} Превышен лимит! Ты можешь участвовать только в {MAX_COVERS_AT_ONCE} каверах одновременно'
ERROR_SAME_COVER = f"{ERROR} У тебя уже записан кавер на данную песню на таком же уровне"
ERROR_EXPIRED = f'{ERROR} Кавер истек %s'
ERROR_DURATION = f'{ERROR} Время записи должно быть от 1 мин до 2 мин'
ERR0R_NOT_CHOSEN = f"{ERROR} Ты не выбрал кавер: {config.panel_command} -> Covers"
ERROR_USER_NOT_FOUND = f'{ERROR} Пользователь не найден'
ERROR_WRONG_PARAMETER = f"{ERROR} Напутал с параметром: %s. Должно быть число."
ERROR_ONLY_FOR_NEWBIES = f"Только для пришедших"
SUCCESS_VOICE_ACCEPTED = f'{OK} Твой кавер на %s принят.\n'
SUCCESS_OK = f'{OK} Сделано!'
WANTS_MORE_POINTS = f'%s с %s ID хочет больше {POINT}'
CHOOSE_COVER = f"Выбери кавер:\n" \
               f"{COVER} - должно быть записано," \
               f"{OK} - записано, " \
               f"{CUR} - текущий/запись."
NO_COVERS = f'{NO} Нету каверов'
CHOOSE_OPTION = 'Выбирай:'
TOP = f'ТОП {TOP} ПОЛЬЗОВАТЕЛЕЙ\n'
LYRICS_TEXT = f"{LYRICS} Текст песни:\n\n%s\n\n"
LYRICS_ERROR = "Не найду текст песни. Попробуй еще раз: выбери кавер в Мои Каверы или записывай без текста"
TIME_LEFT = f"{TIME} Времени осталось до %s"
NOT_ENOUGH_PARTICIPANTS = f"{PARTIC} Не хватает участников(%d/{MIN_COVER_PARTICIPANTS})"
EARLY_BOOST = f'Подожди %d участников или до %s'
POINTS_PRESENT = f"Ты получил {POINT}x%d"
CP_REACHED = f"{RATING} У тебя много опыта, поэтому пришло время проверить твой уровень. " \
             f"Пожалуйста, запиши кавер на %d"
CHANNEL_RATING = f"%d. %s %s. Уровень: %s\nОцени в комментариях 👇👇👇"

PRIVATE_NEW_SONG = f"{NEW_COVER_INDICATOR} %s"
PRIVATE_RATING = f'{PARTIC} Твой кавер на %s оценивается прямо сейчас!'
PRIVATE_WINNER = f'Ты занял %s место в кавере %s. %s {POINT}, +%d {EXP}'
PRIVATE_TIME_TO_RECORD = f"{CLOCK} У тебя {round(SEC_COVERING / 60, 1)} минут, чтобы записать кавер на %s, ставка: %d, учасников: %d, возможный навар: %d"
POLL_RATE = f'Как ты оценишь кавер?'
USER_INFO = f'%s\n' \
                f'Место: %s\n'\
                f'Уровень: %s\n'\
                f'Опыт {EXP}: %s\n'\
                f'Монеты: %d {POINT}\n'\
                f'Жетоны: %d {FAKE_POINT}\n'\
                f'Каверы: {COVER}x%d\n'\
                '\n'
USER_INFO_PRIVATE = f'%s\n' \
                f'Место: %s\n'\
                f'Уровень: %s\n'\
                f'Опыт {EXP}: %s\n'\
                f'Жетоны: %d {FAKE_POINT}\n'\
                f'Каверы: {COVER}x%d\n'\
                '\n'
SUBSCRIBE = f'Подпишись на {config.CHANNEL_NAME}: {config.GROUP_INVITE_LINK}'
DESCRIPTION = f""",
Этот бот даст возможность заработать на своих каверах.
Жми START, чтобы увидеть как это работает.
"""
START = f"""
Если ты хорошо играешь на музыкальном инструменте и вместе с тем хорошо поешь ты можешь получить за это деньги.
Здесь все происходит по типу ставок. На канале {config.GROUP_INVITE_LINK} выбираешь песню, ставишь на себя определенное \
количество очков, далее записываются каверы с помощью этого бота. \ 
Голосованием подписчиков выбирается победитель, который забирает себе победные очки. Впоследствие очки можно обменять в гривны.
Чтобы подробнее ознакомиться  с правилами пиши /cpanel, кнопка Правила.
Подписывайся:
"""
RULES_TEXT = f"""
1. Общие
    Учасники делятся по уровню (любители/профи), только после участия в каверах с жетонами {FAKE_POINT}.
    Кавер записывается только с помощью  голосового сообщения, его длительность должна быть от 1 до 2 минут. 
    Ты должен петь под какой-то музыкальный инструмент САМОСТОЯТЕЛЬНО. Петь под фон не допускается. 
    Голосованием подписчиков выбирается победитель, который забирает себе {WINNER_PERCENTAGE * 100}%. 
    Получить деньги за очки можно будет только при наличии 400 монет и выше. Одна монета - 1 грн. 
2. Важные детали
    Число участников в одном кавере: {MIN_COVER_PARTICIPANTS}-{MAX_COVER_PARTICIPANTS}.
    Важно! Каждый этап кавера ({WANTING} -> {COVERING} -> {RATING}) имеет конечную дату. Когда ты подумаешь, что пора \
двигаться дальше просто выбери этот кавер в Мои Каверы и бот попробует его отправить на новый этап.
    Время чтобы собрать {MAX_COVER_PARTICIPANTS} участников ({WANTING} этап): {round(SEC_WANTING/60, 1)} мин.
    Время для участников, чтобы записать их каверы ({COVERING} этап): {round(SEC_COVERING/60, 1)} мин.
    Время чтобы оценить кавер ({RATING} этап): {round(SEC_RATING/60, 1)} мин.
    Чтобы получить текст песни выбери соответсвующий кавер в Мои Каверы (на этапе covering)
3. Очки
    - победитель забирает всё, кроме {MY_PERCENTAGE*100}%,
    - добавить предпочтительную песню: {settings.COST_ADD_COVER} {POINT} \
(пользуйся инлайн-режимом (@coverTavernBot <поиск песни>)),
4. Опыт
    количество опыта зависит от занимаемого места в кавере:
        {f'- 1: +{EXPERIENCE[0]} {EXP}' if MAX_COVER_PARTICIPANTS == 1 else ''} \
        {f'- 2: +{EXPERIENCE[1]} {EXP}' if MAX_COVER_PARTICIPANTS == 2 else ''} \
        {f'- 3: +{EXPERIENCE[2]} {EXP}' if MAX_COVER_PARTICIPANTS == 3 else ''} \
        {f'- 4: +{EXPERIENCE[3]} {EXP}' if MAX_COVER_PARTICIPANTS == 4 else ''} \
        {f'- 5: +{EXPERIENCE[4]} {EXP}' if MAX_COVER_PARTICIPANTS == 5 else ''} \
        {f'- 6: +{EXPERIENCE[5]} {EXP}' if MAX_COVER_PARTICIPANTS == 6 else ''}
    Опыт нужен для регулярной проверки уровня учасников, и перевода последних на другой уровень.
    Каждый раз когда пересекается порог с определенным количеством опыта {EXP}, один из последних каверов 
    будет оцениваться по уровню, и в зависимости от оценки определять уровень учасника. Вот эти пороги:
    {str(LVL_UPGRADE_SCHEME).strip('[]')}
"""
MY_STATISTICS = f"Моя статистика {STAT}"
MY_COVERS = f"Мои каверы {COVER}"
GET_POINTS = f"Получить очки {POINT}"
TOP_10 = f"Топ {settings.TOP} {WINNER}"
RULES_ = f"Правила {RULES}"
BACK_ = '<< Назад'
INFO_ = f"Инфо {INFO}"
NEXT_ = 'Вперед >>'
ADMIN_DIRECT = f"Пиши сюда: {config.ADMIN_USERNAME}. ID: %s"
MUST_PLAY = "В начале у тебя есть пробные очки, которые ты можешь поставить вместо обычных очков, чтобы вникнуть в игру. Потом жди, когда твой уровень будет известен"

COVER_ADDED_PRIVATE = f"{NEW_COVER_INDICATOR} %s\nПревью: %s"
COVER_ADDED_PUBLIC = f"%s. {NEW_COVER_INDICATOR_CHANNEL} %s\nМинимальная cтавка: {MIN_POINTS} %s\nУровень: %s\nПревью: %s\nУчаствуй в комментариях 👇"




def _(text, lang=None, *args):
    return text

    # if lang in ['ru', 'uk']:
    #     formatted_string = VOCABULARY['ru'][text]
    #     return formatted_string
    # else:
    #     formatted_string = VOCABULARY['en'][text]
    #     return formatted_string

