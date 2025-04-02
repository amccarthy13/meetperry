from resources.postgres import PostgreSQL


class DataManager(object):
    def __init__(self, postgres: PostgreSQL = None, *args, **kwargs):
        self.postgres = postgres
