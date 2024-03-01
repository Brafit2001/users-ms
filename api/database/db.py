import traceback

import mariadb
from decouple import config

from api.utils.Logger import Logger


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
        Logger.add_to_log("error", str(ex))
        Logger.add_to_log("error", traceback.format_exc())
        raise
