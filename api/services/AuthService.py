import traceback

from werkzeug.security import check_password_hash

# Database
from api.database.db import get_connection
from api.models.PermissionModel import row_to_permission
# Models
from api.models.UserModel import row_to_user
# Logger
from api.utils.Logger import Logger


class AuthService:

    @classmethod
    def login_user(cls, user):
        try:
            connection_dbusers = get_connection('dbusers')
            authenticated_user = None
            with (connection_dbusers.cursor() as cursor_dbusers):
                query = "select * from users where username = '{}'".format(
                    user.username)
                cursor_dbusers.execute(query)
                row = cursor_dbusers.fetchone()
                Logger.add_to_log("info" ,row )
                check_password = check_password_hash(pwhash=row[2], password=user.password)
                if check_password is False:
                    return authenticated_user
                if row is not None:
                    authenticated_user = row_to_user(row=row)
            connection_dbusers.close()
            return authenticated_user
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_permissions(cls, userid):
        try:
            connection_dbusers = get_connection('dbusers')
            permissions_list = []
            with (connection_dbusers.cursor() as cursor_dbusers):
                query = ("SELECT permission, permission_type "
                         "FROM relationusersroles a INNER JOIN relationrolespermissions b ON a.role = b.role "
                         "WHERE a.`user` = '{}'").format(userid)
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
            raise


