import traceback
from http import HTTPStatus

import mariadb

from api.database.db import get_connection
from api.models.UserModel import User, UserData
from api.utils.AppExceptions import EmptyDbException, NotFoundException
from api.utils.Logger import Logger


class UserService:

    @classmethod
    def get_all_users(cls) -> list[UserData]:
        try:
            connection_dbusers = get_connection('dbusers')
            users_list = []
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = "select * from users"
                cursor_dbusers.execute(query)
                resultset = cursor_dbusers.fetchall()
                if not resultset:
                    raise EmptyDbException("No users found")
                for row in resultset:
                    user = to_user_data(row)
                    users_list.append(user)
            connection_dbusers.close()
            return users_list
        except EmptyDbException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())

    @classmethod
    def get_user_by_id(cls, userId: int) -> User:
        try:
            connection_dbusers = get_connection('dbusers')
            user = None
            with connection_dbusers.cursor() as cursor_dbusers:
                query = "select * from users where id = '{}'".format(userId)
                cursor_dbusers.execute(query)
                row = cursor_dbusers.fetchone()
                if row is not None:
                    user = to_user(row)
            connection_dbusers.close()
            return user
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())

    @classmethod
    def add_user(cls, user: User):
        try:
            connection_dbusers = get_connection('dbusers')
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = ("insert into users set username = '{}',password = '{}', name = '{}' ,surname = '{}', "
                         "email = '{}'").format(
                    user.username,
                    user.password,
                    user.name,
                    user.surname,
                    user.email
                )
                cursor_dbusers.execute(query)
                connection_dbusers.commit()
            connection_dbusers.close()
            return 'User added'
        except mariadb.IntegrityError:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())

    @classmethod
    def delete_user(cls, userId: int):
        try:
            userExist = cls.get_user_by_id(userId)
            if userExist is None:
                raise NotFoundException("User not Found")
            connection_dbusers = get_connection('dbusers')
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = "delete from users where id = '{}'".format(userId)
                cursor_dbusers.execute(query)
                connection_dbusers.commit()
            connection_dbusers.close()
            return f'User {userId} deleted'
        except NotFoundException:
            raise
        except Exception as ex:
            print(ex)

    @classmethod
    def update_user(cls, user: User):
        try:
            userExist = cls.get_user_by_id(user.id)
            if userExist is None:
                raise NotFoundException("User not Found")
            connection_dbusers = get_connection('dbusers')
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = ("update users set username = '{}',password = '{}', name = '{}' ,surname = '{}', email = '{}' "
                         "where id = '{}'").format(
                    user.username,
                    user.password,
                    user.name,
                    user.surname,
                    user.email,
                    user.id
                )
                cursor_dbusers.execute(query)
                connection_dbusers.commit()
            connection_dbusers.close()
            return f'User {user.id} updated'
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())


def to_user_data(row) -> UserData:
    return UserData(
        idUser=row[0],
        group=row[1],
        username=row[2],
        name=row[4],
        surname=row[5],
        email=row[6],
        image=row[7]
    )


def to_user(row) -> User:
    return User(
        idUser=row[0],
        group=row[1],
        username=row[2],
        password=row[3],
        name=row[4],
        surname=row[5],
        email=row[6],
        image=row[7]
    )
