from services.database import Artist, session
from sqlalchemy import delete

class Artists:
    @staticmethod
    def get_favorite_artists(user_id):
        artists = session.query(Artist).filter_by(telegramUserID=user_id).all()
        return artists

    @staticmethod
    def add_favorite_artist(user_id, artist_name, spotify_id):
        artist = Artist(telegramUserID=user_id, artist_name=artist_name, spotifyID=spotify_id)
        session.add(artist)
        session.commit()

    @staticmethod
    def del_favorite_artist(user_id, spotify_id):
        artist_to_delete = session.query(Artist).filter_by(telegramUserID=user_id, spotifyID=spotify_id).first()
        if artist_to_delete:
            session.delete(artist_to_delete)
            session.commit()

    @staticmethod
    def del_favorite_artists(user_id):
        delete_statement = delete(Artist).where(Artist.telegramUserID==user_id)
        session.execute(delete_statement)
        session.commit()

    @staticmethod
    def get_artists(user_id=None):
        if user_id:
            return session.query(Artist).filter_by(telegramUserID=user_id).all()
        else:
            artists = session.query(Artist).all()
            return artists