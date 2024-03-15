import random
import string
import traceback

import mariadb
from werkzeug.security import generate_password_hash

from api.database.db import get_connection
from api.models.PermissionModel import row_to_permission
from api.models.UserModel import User, row_to_user
from api.utils.AppExceptions import EmptyDbException, NotFoundException
from api.utils.Logger import Logger
from api.utils.QueryParameters import QueryParameters


class UserService:

    @classmethod
    def get_all_users(cls, params: QueryParameters) -> list[User]:
        try:
            connection_dbusers = get_connection('dbusers')
            users_list = []
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = "select * from users"
                query = params.add_to_query(query)
                cursor_dbusers.execute(query)
                result_set = cursor_dbusers.fetchall()
                if not result_set:
                    raise EmptyDbException("No users found")
                for row in result_set:
                    user = row_to_user(row)
                    users_list.append(user)
            connection_dbusers.close()
            return users_list
        except mariadb.OperationalError:
            raise
        except EmptyDbException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

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
                    user = row_to_user(row)
                else:
                    raise NotFoundException("User not found")
            connection_dbusers.close()
            return user
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_user_by_username(cls, username: str) -> User:
        try:
            connection_dbusers = get_connection('dbusers')
            user = None
            with connection_dbusers.cursor() as cursor_dbusers:
                query = "select * from users where username = '{}'".format(username)
                cursor_dbusers.execute(query)
                row = cursor_dbusers.fetchone()
                if row is not None:
                    user = row_to_user(row)
                else:
                    raise NotFoundException("User not found")
            connection_dbusers.close()
            return user
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def add_user(cls, user: User):
        try:
            connection_dbusers = get_connection('dbusers')
            password = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase +
                                              string.digits, k=6))
            user.password = password
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = ("insert into users set username = '{}',password = '{}', name = '{}' ,surname = '{}', "
                         "email = '{}'").format(
                    user.username,
                    generate_password_hash(user.password),
                    user.name,
                    user.surname,
                    user.email
                )
                cursor_dbusers.execute(query)
                connection_dbusers.commit()

                query = "select * from users where username = '{}'".format(user.username)
                cursor_dbusers.execute(query)
                user_id = cursor_dbusers.fetchone()[0]

            connection_dbusers.close()
            return user_id
        except mariadb.IntegrityError:
            # User already exists
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def delete_user(cls, userId: int):
        try:
            # Check if user exists
            cls.get_user_by_id(userId)
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
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def update_user(cls, user: User):
        try:
            # Check if user exists
            cls.get_user_by_id(user.id)
            connection_dbusers = get_connection('dbusers')
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = ("update users set username = '{}', name = '{}' ,surname = '{}', email = '{}' "
                         "where id = '{}'").format(
                    user.username,
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
            raise

    @classmethod
    def send_password_email(cls, user):
        try:
            pass
            '''
            email_sender =             email_sender = 'no.reply.clipclass@gmail.com'
            credential = app.config['EMAIL_PASSWORD']
            email_receiver = email
            credential = app.config['EMAIL_PASSWORD']
            email_receiver = email
            '''
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_user_role(cls, userId: int):
        try:
            connection_dbusers = get_connection('dbusers')
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = "select * from relationusersroles where user = '{}'".format(userId)
                cursor_dbusers.execute(query)
                row = cursor_dbusers.fetchone()
                if row is not None:
                    roleId = row[1]
                else:
                    raise NotFoundException("No roles found")
            connection_dbusers.close()
            return roleId
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_user_permissions(cls, userId: int):
        try:
            connection_dbusers = get_connection('dbusers')
            user_role = cls.get_user_role(userId)
            permissions_list = []
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = "select * from relationrolespermissions where role = '{}'".format(user_role)
                cursor_dbusers.execute(query)
                result_set = cursor_dbusers.fetchall()
                if not result_set:
                    raise EmptyDbException("No permissions found")
                for row in result_set:
                    permission = row_to_permission(row)
                    permissions_list.append(permission.to_tuple())
            connection_dbusers.close()
            return permissions_list
        except EmptyDbException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def assign_group(cls, userId: int, groupId: int):
        try:
            connection_dbgroups = get_connection('dbgroups')
            with connection_dbgroups.cursor() as cursor_dbgroups:
                query = "insert into relationusersgroups set user='{}', `group`='{}'".format(userId, groupId)
                cursor_dbgroups.execute(query)
                connection_dbgroups.commit()
            connection_dbgroups.close()
            return 'User was assigned to group successfully'
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise
