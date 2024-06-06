from sqlalchemy import func

from settings import TOP
from services.database import session, User


class Users:
    @staticmethod
    def get_user_by_id(user_id):
        user = session.query(User).filter_by(telegramUserID=user_id).one()
        return user

    @staticmethod
    def get_user_by_username(username):
        user = session.query(User).filter_by(username=username).one()
        return user

    @staticmethod
    def add_new_user(user_id, username, lang):
        user = User(telegramUserID=user_id, username=f'@{username}' if username else None, lang=lang)
        session.add(user)
        session.commit()
        return user

    @staticmethod
    def add_points(user_id, points=0, to_all=False):
        if not to_all:
            session.query(User).filter_by(telegramUserID=user_id).update({User.points: User.points + points})
        else:
            session.query(User).update({User.points: User.points + points})

        session.commit()

    @staticmethod
    def set_level_experience(user_id, level, exp=0):
        session.query(User).filter(User.telegramUserID == user_id).update({'level': level, 'experience': exp})
        session.commit()

    @staticmethod
    def get_user_place(user_id):
        query = session.query(User, func.row_number().over(order_by=[User.level.desc(), User.experience.desc()]).label(
            'row_number')).filter(User.telegramUserID == user_id)
        result = query.one()
        return result.row_number

    @staticmethod
    def get_top_users(limit=TOP):
        query = session.query(User, func.row_number().over(order_by=[User.level.desc(), User.experience.desc()]).label(
            'row_number')).limit(limit)
        result = query.all()
        return result

    @staticmethod
    def get_users_count():
        count = session.query(User).count()
        return count

    @staticmethod
    def get_users(offset, limit=20):
        return session.query(User).order_by(User.username.desc()).offset(offset*limit).all()

    @staticmethod
    def get_user_by_poll_id(poll_id):
        print(poll_id)
        return session.query(User).filter(User.ratingPollID == poll_id).one()
