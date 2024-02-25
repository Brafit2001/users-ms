import mariadb


def get_connection(database):
    try:
        return mariadb.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='9412',
            database=database
        )
    except Exception as ex:
        print(ex)
