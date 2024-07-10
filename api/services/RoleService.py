import traceback

import mariadb

from api.database.db import get_connection
from api.models.PermissionModel import Permission, row_to_permission, PermissionType
from api.models.RoleModel import Role, row_to_role
from api.models.UserModel import User, row_to_user
from api.utils.AppExceptions import EmptyDbException, NotFoundException
from api.utils.Logger import Logger
from api.utils.QueryParameters import QueryParameters


class RoleService:

    @classmethod
    def get_all_roles(cls, params: QueryParameters) -> list[Role]:
        try:
            connection_dbusers = get_connection('dbusers')
            roles_list = []
            with connection_dbusers.cursor() as cursor_dbusers:
                query = "select * from roles"
                query = params.add_to_query(query)
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
    def get_role_by_name(cls, name: str) -> Role:
        try:
            connection_dbusers = get_connection('dbusers')
            role = None
            with connection_dbusers.cursor() as cursor_dbusers:
                query = "select * from roles where name = '{}'".format(name)
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
            raise

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
    def delete_role_user(cls, roleId: int, userId: int):
        try:
            connection_dbusers = get_connection('dbusers')
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = "delete from relationusersroles where `role` = '{}' and user = '{}'".format(roleId, userId)
                cursor_dbusers.execute(query)
                connection_dbusers.commit()
            connection_dbusers.close()
            return f'User {userId} from Role {roleId} has been deleted'
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def delete_role_permission(cls, roleId: int, permissionId: int, permissionType: PermissionType):
        try:
            connection_dbusers = get_connection('dbusers')
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = ("delete from relationrolespermissions "
                         "where `role` = '{}' "
                         "and permission = '{}' "
                         "and permission_type = '{}' ").format(roleId, permissionId, permissionType.value)
                cursor_dbusers.execute(query)
                connection_dbusers.commit()
            connection_dbusers.close()
            return f'Permission {permissionId} from Role {roleId} has been deleted'
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

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

    @classmethod
    def assign_role(cls, userId: int, roleId: int):
        try:
            connection_dbusers = get_connection('dbusers')
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = "insert into relationusersroles set user = '{}', role = '{}'".format(userId, roleId)
                cursor_dbusers.execute(query)
                connection_dbusers.commit()
            connection_dbusers.close()
            return 'User added to role'
        except mariadb.IntegrityError:
            # User has already the role
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def assign_permission(cls, roleId: int, permissionType: int ,permissionId: int):
        try:
            connection_dbusers = get_connection('dbusers')
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = ("insert into relationrolespermissions "
                         "set role = '{}', "
                         "permission = '{}', permission_type = '{}'").format(roleId, permissionId, permissionType)
                cursor_dbusers.execute(query)
                connection_dbusers.commit()
            connection_dbusers.close()
            return 'Permission added to role'
        except mariadb.IntegrityError as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            # Role has already the permission
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_role_users(cls, roleId: int) -> list[User]:
        try:
            connection_dbusers = get_connection('dbusers')
            users_list = []
            with connection_dbusers.cursor() as cursor_dbusers:
                query = ("SELECT id, username, PASSWORD, NAME, surname, email, image FROM relationusersroles a "
                         "INNER JOIN users b ON a.user = b.id WHERE ROLE = '{}'").format(roleId)
                cursor_dbusers.execute(query)
                result_set = cursor_dbusers.fetchall()
                if not result_set:
                    raise EmptyDbException("No users found")
                for row in result_set:
                    user = row_to_user(row)
                    users_list.append(user)
            connection_dbusers.close()
            return users_list
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_role_remaining_users(cls, roleId: int) -> list[User]:
        try:
            connection_dbusers = get_connection('dbusers')
            users_list = []
            with connection_dbusers.cursor() as cursor_dbusers:
                query = ("SELECT c.id, c.username, c.PASSWORD, c.NAME, c.surname, c.email, c.image FROM users c "
                         "LEFT JOIN (SELECT id, username, PASSWORD, NAME, surname, email, image "
                         "FROM relationusersroles a INNER JOIN users b ON a.user = b.id WHERE ROLE = '{}')"
                         "d ON c.id = d.id WHERE d.id IS NULL").format(roleId)
                cursor_dbusers.execute(query)
                result_set = cursor_dbusers.fetchall()
                if not result_set:
                    raise EmptyDbException("No users found")
                for row in result_set:
                    user = row_to_user(row)
                    users_list.append(user)
            connection_dbusers.close()
            return users_list
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_role_permissions(cls, roleId: int) -> list[Permission]:
        try:
            connection_dbusers = get_connection('dbusers')
            permissions_list = []
            with connection_dbusers.cursor() as cursor_dbusers:
                query = ("SELECT id, permission_type FROM relationrolespermissions a "
                         "INNER JOIN permissions b ON a.permission = b.id WHERE ROLE = '{}'").format(roleId)
                cursor_dbusers.execute(query)
                result_set = cursor_dbusers.fetchall()
                if not result_set:
                    raise EmptyDbException("No permissions found")
                for row in result_set:
                    permission = row_to_permission(row)
                    permissions_list.append(permission)
            connection_dbusers.close()
            return permissions_list
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_role_remaining_permissions(cls, roleId: int) -> list[Permission]:
        try:
            connection_dbusers = get_connection('dbusers')
            permissions_list = []
            with connection_dbusers.cursor() as cursor_dbusers:
                query = ("SELECT c.id FROM permissions c "
                         "LEFT JOIN(SELECT id, permission_type FROM relationrolespermissions a "
                         "INNER JOIN permissions b ON a.permission = b.id WHERE ROLE = '{}')"
                         "d ON c.id = d.id WHERE d.id IS NULL").format(roleId)
                cursor_dbusers.execute(query)
                result_set = cursor_dbusers.fetchall()
                if not result_set:
                    raise EmptyDbException("No permissions found")
                for row in result_set:
                    # READ
                    aux1 = (row[0], 0)
                    permission = row_to_permission(aux1)
                    permissions_list.append(permission)
                    # WRITE
                    aux2 = (row[0], 1)
                    permission = row_to_permission(aux2)
                    permissions_list.append(permission)
            connection_dbusers.close()
            return permissions_list
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise