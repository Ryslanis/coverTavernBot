import datetime

from settings import *
from services.database import session, Cover, Voice


class Covers:
    @staticmethod
    def add_cover(artist, song, level, status, user_id, preview_url='', points=50, partcipantsCount=0, postID=None):
        new_cover = Cover(artist=artist, song=song, creator=user_id, level=level, status=status,
                          targetDate=datetime.datetime.now() + datetime.timedelta(seconds=SEC_WANTING),
                          participationsCount=partcipantsCount, previewUrl=preview_url, points=points,
                          postID=postID)
        session.add(new_cover)
        session.commit()
        return new_cover

    @staticmethod
    def get_cover_by_id(cover_id):
        cover = session.query(Cover).filter_by(id=cover_id).one()
        return cover

    @staticmethod
    def get_cover_by_rating__poll_id(poll_id):
        cover = session.query(Cover).filter_by(ratingPollID=poll_id).one()
        return cover

    @staticmethod
    def get_covers_count():
        return session.query(Cover).count()

    @staticmethod
    def get_wantings(user_id, level, offset, limit=4):
        voices = session.query(Cover, Voice).join(Cover, Cover.id == Voice.coverID). \
            filter(Cover.level == level).order_by(Cover.created_on.desc()).offset(offset * limit).limit(
                limit).all()
        return voices
