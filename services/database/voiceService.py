import random

from sqlalchemy import and_, func

from services.database import session, Voice, Cover, User
from settings import LAST_VOICES


class Voices:
    @staticmethod
    def add_voice(user_id, cover_id, points=0):
        session.query(Voice).filter(Voice.telegramUserID == user_id).update({'current': False})
        session.commit()

        voice = Voice(telegramUserID=user_id, coverID=cover_id, current=True, points=points)
        session.add(voice)
        session.commit()
        return voice

    @staticmethod
    def get_voice_by_id(voice_id):
        voices = session.query(Voice).filter_by(id=voice_id).one()
        return voices

    @staticmethod
    def get_voices(user_id):
        voices = session.query(Voice).filter_by(telegramUserID=user_id).order_by(Voice.created_on.desc()).all()
        return voices

    @staticmethod
    def get_voices_join_cover(user_id, offset, limit=4):
        if limit:
            voices = session.query(Cover, Voice).join(Cover, Cover.id == Voice.coverID). \
                filter(Voice.telegramUserID == user_id).order_by(Voice.created_on.desc()).offset(offset * limit).limit(
                limit).all()
        else:
            voices = session.query(Cover, Voice).join(Cover, Cover.id == Voice.coverID). \
                filter(Voice.telegramUserID == user_id).order_by(Voice.created_on.desc()).all()
        return voices

    @staticmethod
    def get_voices_join_user(voice_id, user_id):
        voices = session.query(Voice, User).join(Voice, Voice.telegramUserID == User.telegramUserID).filter(
            Voice.id == voice_id).one()
        return voices

    @staticmethod
    def get_voice(cover_id, user_id):
        voice = session.query(Voice).filter_by(telegramUserID=user_id, coverID=cover_id).one()
        return voice

    @staticmethod
    def delete_voice(voice_id):
        session.query(Voice).filter_by(id=voice_id).delete()

    @staticmethod
    def get_active_voice(user_id):
        voice = session.query(Voice).filter_by(telegramUserID=user_id, current=True).one()
        return voice

    # newbie
    @staticmethod
    def get_voice_by_cover_id(cover_id):
        voices = session.query(Voice).filter_by(coverID=cover_id).one()
        return voices

    # @staticmethod
    # def get_voices_by_cover_id(cover_id):
    #     cover = session.query(Cover).filter_by(id=cover_id)
    #     top_points_number, top_points_count = Voices.get_same_points_count(cover_id)
    #     voices = session.query(Voice).filter_by(coverID=cover_id).order_by(Voice.id).all()
    #     return voices

    @staticmethod
    def get_voices_count(user_id=None):
        if user_id:
            count = session.query(Voice).filter_by(telegramUserID=user_id).count()
        else:
            count = session.query(Voice).count()
        return count

    @staticmethod
    def set_voice_recording(voice_id, user_id):
        session.query(Voice).filter(Voice.telegramUserID == user_id).update({'current': False})
        session.commit()
        session.query(Voice).filter(and_(Voice.id == voice_id, user_id == user_id)).update({'current': True})
        session.commit()

    @staticmethod
    def get_unrecorded_voices(user_id):
        return session.query(Voice).filter(Voice.telegramUserID == user_id, Voice.recorded == False).all()

    @staticmethod
    def get_recorded_voices(user_id):
        return session.query(Voice).filter(Voice.telegramUserID == user_id, Voice.recorded == True).all()

    @staticmethod
    def get_points_count(cover_id, points):
        return session.query(Voice).filter_by(coverID=cover_id, points=points).count()

    @staticmethod
    def get_voices_by_cover_id(cover_id):
        points = session.query(Voice.points). \
            filter_by(coverID=cover_id). \
            group_by(Voice.points). \
            order_by(func.count(Voice.points).desc()).first()
        if points:
            return session.query(Voice).filter_by(coverID=cover_id, points=points[0]).all()

    @staticmethod
    def get_last_random_voice(user_id):
        voices = session.query(Voice).filter(Voice.telegramUserID == user_id, Voice.telegramVoiceID != None).order_by(
            Voice.id.desc()).limit(LAST_VOICES).all()
        if len(voices) < LAST_VOICES:
            return
        return random.choice(voices)
