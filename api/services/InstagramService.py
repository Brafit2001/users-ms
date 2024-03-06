import traceback

from api.database.db import get_connection
from api.models.InstagramModel import Instagram
from api.utils.AppExceptions import NotFoundException
from api.utils.Logger import Logger
from instagrapi import Client


class InstagramService:
    instaClient = Client()

    @classmethod
    def login(cls, instaUser: Instagram):
        try:
            user_logged = cls.check_login(instaUser)
            if user_logged is not False:
                return user_logged
            connection_dbusers = get_connection('dbusers')
            cls.instaClient.login(instaUser.instagramUser, instaUser.password)
            sessionId = cls.instaClient.get_settings()["authorization_data"]["sessionid"]
            with connection_dbusers.cursor() as cursor_dbusers:
                query = "insert into instagram set user = '{}', session = '{}', instagramuser = '{}'".format(
                    instaUser.clipclassUser,
                    sessionId,
                    instaUser.instagramUser
                )
                instaUser.session = sessionId
                cursor_dbusers.execute(query)
                connection_dbusers.commit()
            connection_dbusers.close()
            return instaUser

        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def check_login(cls, instaUser):
        try:
            connection_dbusers = get_connection('dbusers')
            with connection_dbusers.cursor() as cursor_dbusers:
                query = "select * from instagram where user = '{}'".format(instaUser.clipclassUser)
                cursor_dbusers.execute(query)
                row = cursor_dbusers.fetchone()
                if row is not None:
                    connection_dbusers.close()
                    return row_to_instagram(row)
            connection_dbusers.close()
            return False

        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def logout(cls, instaUser):
        try:
            user_logged = cls.check_login(instaUser)
            if user_logged is False:
                raise NotFoundException("User is not logged in the platform")
            cls.instaClient.login_by_sessionid(instaUser.session)
            cls.instaClient.logout()
            connection_dbusers = get_connection('dbusers')
            with connection_dbusers.cursor() as cursor_dbusers:
                query = "delete from instagram where user = '{}'".format(instaUser.clipclassUser)
                cursor_dbusers.execute(query)
                connection_dbusers.commit()
            connection_dbusers.close()
            return True
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

def row_to_instagram(row):
    return Instagram(
        clipclassUser=row[0],
        session=row[1],
        instagramUser=row[2])
