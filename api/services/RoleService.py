import traceback

import mariadb

from api.database.db import get_connection
from api.models.RoleModel import Role
from api.utils.AppExceptions import EmptyDbException, NotFoundException
from api.utils.Logger import Logger


class RoleService:

    @classmethod
    def get_all_roles(cls) -> list[Role]:
        try:
            connection_dbusers = get_connection('dbusers')
            roles_list = []
            with connection_dbusers.cursor() as cursor_dbusers:
                query = "select * from roles"
                cursor_dbusers.execute(query)
                result_set = cursor_dbusers.fetchall()
                if not result_set:
                    raise EmptyDbException("No roles found")
                for row in result_set:
                    role = row_to_role(row)
                    roles_list.append(role)
            connection_dbusers.close()
            return roles_list
        except EmptyDbException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())

    @classmethod
    def get_role_by_id(cls, roleId: int) -> Role:
        try:
            connection_dbusers = get_connection('dbusers')
            role = None
            with connection_dbusers.cursor() as cursor_dbusers:
                query = "select * from roles where id = '{}'".format(roleId)
                cursor_dbusers.execute(query)
                row = cursor_dbusers.fetchone()
                if row is not None:
                    role = row_to_role(row)
                else:
                    raise NotFoundException("Role not found")
            connection_dbusers.close()
            return role
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())

    @classmethod
    def add_role(cls, role: Role):
        try:
            connection_dbusers = get_connection('dbusers')
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = "insert into roles set name = '{}'".format(role.name)
                cursor_dbusers.execute(query)
                connection_dbusers.commit()
            connection_dbusers.close()
            return 'Role added'
        except mariadb.IntegrityError:
            # Role already exists
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())

    @classmethod
    def delete_role(cls, roleId: int):
        try:
            # Check if user exists
            role_deleted = cls.get_role_by_id(roleId)
            connection_dbusers = get_connection('dbusers')
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = "delete from roles where id = '{}'".format(roleId)
                cursor_dbusers.execute(query)
                connection_dbusers.commit()
            connection_dbusers.close()
            return role_deleted
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())

    @classmethod
    def update_role(cls, role: Role):
        try:
            # Check if user exists
            cls.get_role_by_id(role.id)
            connection_dbusers = get_connection('dbusers')
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = "update roles set name = '{}' where id = '{}'".format(role.name, role.id)
                cursor_dbusers.execute(query)
                connection_dbusers.commit()
            connection_dbusers.close()
            return 'OK'
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())


def row_to_role(row) -> Role:
    return Role(
        idRole=row[0],
        name=row[1]
    )
