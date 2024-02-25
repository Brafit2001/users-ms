import traceback

# Database
from api.database.db import get_connection
# Logger
from api.utils.Logger import Logger
# Models
from api.models.UserModel import User


class AuthService:

    @classmethod
    def login_user(cls, user):
        try:
            connection_dbusers = get_connection('dbusers')
            authenticated_user = None
            with (connection_dbusers.cursor() as cursor_dbusers):
                query = "select * from users where username = '{}' and password = '{}'".format(
                    user.username, user.password)
                cursor_dbusers.execute(query)
                row = cursor_dbusers.fetchone()
                if row is not None:
                    authenticated_user = User(
                        idUser=row[0],
                        group=row[1],
                        username=row[2],
                        password=row[3],
                        name=row[4],
                        surname=row[5],
                        email=row[6],
                        image=row[7]
                    )
            connection_dbusers.close()
            return authenticated_user
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
