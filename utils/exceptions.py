class LevelAccordanceError(Exception):
    def __init__(self, user):
        self.user = user


class CoverExpiredError(Exception):
    def __init__(self, cover):
        self.cover = cover


class NoPointError(Exception):
    pass


class MaxParticipationsError(Exception):
    def __init__(self, cover):
        self.cover = cover


class MinParticipationsError(Exception):
    def __init__(self, cover):
        self.cover = cover


class WrongVoiceDuration(Exception):
    def __init__(self, duration):
        self.duration = duration


class TooManyCoversError(Exception):
    pass


class TheSameCover(Exception):
    pass

class OnlyForNewbies(Exception):
    pass