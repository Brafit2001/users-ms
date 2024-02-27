import mariadb
from decouple import config


def get_connection(database):
    try:
        return mariadb.connect(
            host=config('MARIADB_HOST'),
            port=int(config('MARIADB_PORT')),
            user=config('MARIADB_USER'),
            password=config('MARIADB_PASSWORD'),
            database=database
        )
    except Exception as ex:
        print(ex)
