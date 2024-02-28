import traceback

# Database
from api.database.db import get_connection
from api.models.PermissionModel import Permission, PermissionType
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

    @classmethod
    def get_permissions(cls, idUser):
        try:
            connection_dbusers = get_connection('dbusers')
            permissions_list = []
            with (connection_dbusers.cursor() as cursor_dbusers):
                query = ("SELECT permission, permission_type "
                         "FROM relationusersroles a INNER JOIN relationrolespermissions b ON a.role = b.role "
                         "WHERE a.`user` = '{}'").format(idUser)
                cursor_dbusers.execute(query)
                result_set = cursor_dbusers.fetchall()
                for row in result_set:
                    permission = row_to_permission(row)
                    permissions_list.append(permission.to_tuple())
            connection_dbusers.close()
            return permissions_list
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())


def row_to_permission(row):
    return Permission(
        idPermission=row[0],
        permission_type=PermissionType(row[1])
    )
