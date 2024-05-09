import random
import string
import traceback
from typing import List

import mariadb
from werkzeug.security import generate_password_hash

from api.database.db import get_connection
from api.models import ClassModel
from api.models.CourseModel import row_to_course, Course
from api.models.GroupModel import row_to_group, Group
from api.models.PermissionModel import row_to_permission
from api.models.RoleModel import row_to_role, Role
from api.models.SubjectModel import row_to_subject
from api.models.TopicModel import Topic, row_to_topic
from api.models.UserModel import User, row_to_user
from api.utils.AppExceptions import EmptyDbException, NotFoundException
from api.utils.Logger import Logger
from api.utils.QueryParameters import QueryParameters
from api.services.RoleService import RoleService


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
    def get_user_roles(cls, userId: int) -> list[Role]:
        try:
            connection_dbusers = get_connection('dbusers')
            roles_list = []
            with connection_dbusers.cursor() as cursor_dbusers:
                query = ("SELECT id, name FROM relationusersroles a INNER JOIN roles b ON a.role = b.id WHERE USER = "
                         "'{}'").format(userId)
                cursor_dbusers.execute(query)
                result_set = cursor_dbusers.fetchall()
                if not result_set:
                    raise EmptyDbException("No roles found")
                for row in result_set:
                    role = row_to_role(row)
                    roles_list.append(role)
            connection_dbusers.close()
            return roles_list
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_user_remaining_roles(cls, userId: int) -> list[Role]:
        try:
            connection_dbusers = get_connection('dbusers')
            roles_list = []
            with connection_dbusers.cursor() as cursor_dbusers:
                query = ("SELECT c.id, c.name FROM roles c LEFT JOIN "
                         "(SELECT id, name FROM relationusersroles a "
                         "INNER JOIN roles b ON a.role = b.id WHERE USER = '{}') "
                         "d ON c.id = d.id WHERE d.id IS null").format(userId)
                cursor_dbusers.execute(query)
                result_set = cursor_dbusers.fetchall()
                if not result_set:
                    raise EmptyDbException("No roles found")
                for row in result_set:
                    role = row_to_role(row)
                    roles_list.append(role)
            connection_dbusers.close()
            return roles_list
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_user_courses(cls, userId: int) -> list[Course]:
        try:
            connection_dbgroups = get_connection('dbgroups')
            courses_list = []
            with connection_dbgroups.cursor() as cursor_dbgroups:
                query = ("SELECT DISTINCT * FROM dbcourses.courses g "
                         "INNER JOIN ( SELECT course FROM dbcourses.subjects e "
                         "INNER JOIN(SELECT `subject` FROM dbcourses.classes c "
                         "INNER JOIN(SELECT class FROM relationusersgroups a "
                         "INNER JOIN `groups` b ON a.group = b.id WHERE USER = '{}') d "
                         "ON c.id = d.class)f ON e.id = f.`subject`) h ON g.id = h.course").format(userId)
                cursor_dbgroups.execute(query)
                result_set = cursor_dbgroups.fetchall()
                if not result_set:
                    raise EmptyDbException("No courses found")
                for row in result_set:
                    course = row_to_course(row)
                    courses_list.append(course)
            connection_dbgroups.close()
            return courses_list
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_user_subjects(cls, userId: int) -> list[Course]:
        try:
            connection_dbgroups = get_connection('dbgroups')
            subjects_list = []
            with connection_dbgroups.cursor() as cursor_dbgroups:
                query = ("SELECT DISTINCT e.* FROM dbcourses.subjects e "
                         "INNER JOIN(SELECT `subject` FROM dbcourses.classes c "
                         "INNER JOIN(SELECT class FROM relationusersgroups a "
                         "INNER JOIN `groups` b ON a.group = b.id WHERE USER = '{}') d "
                         "ON c.id = d.class)f ON e.id = f.`subject`").format(userId)
                cursor_dbgroups.execute(query)
                result_set = cursor_dbgroups.fetchall()
                if not result_set:
                    raise EmptyDbException("No subjects found")
                for row in result_set:
                    subject = row_to_subject(row)
                    subjects_list.append(subject)
            connection_dbgroups.close()
            return subjects_list
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_user_classes(cls, userId: int) -> list[ClassModel]:
        try:
            connection_dbgroups = get_connection('dbgroups')
            classes_list = []
            with connection_dbgroups.cursor() as cursor_dbgroups:
                query = ("SELECT DISTINCT c.* FROM dbcourses.classes c "
                         "INNER JOIN(SELECT class FROM relationusersgroups a "
                         "INNER JOIN `groups` b ON a.group = b.id WHERE USER = '{}') d "
                         "ON c.id = d.class").format(userId)
                cursor_dbgroups.execute(query)
                result_set = cursor_dbgroups.fetchall()
                if not result_set:
                    raise EmptyDbException("No classes found")
                for row in result_set:
                    class_item = row_to_subject(row)
                    classes_list.append(class_item)
            connection_dbgroups.close()
            return classes_list
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_user_groups(cls, userId: int) -> list[Group]:
        try:
            connection_dbgroups = get_connection('dbgroups')
            groups_list = []
            with connection_dbgroups.cursor() as cursor_dbgroups:
                query = ("SELECT id, NAME, DESCRIPTION, class FROM relationusersgroups a INNER JOIN `groups` b ON "
                         "a.group = b.id WHERE USER = '{}'").format(userId)
                cursor_dbgroups.execute(query)
                result_set = cursor_dbgroups.fetchall()
                if not result_set:
                    raise EmptyDbException("No groups found")
                for row in result_set:
                    group = row_to_group(row)
                    groups_list.append(group)
            connection_dbgroups.close()
            return groups_list
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_user_topics(cls, userId: int) -> list[Topic]:
        try:
            connection_dbgroups = get_connection('dbgroups')
            topics_list = []
            with connection_dbgroups.cursor() as cursor_dbgroups:
                query = ("SELECT c.* FROM topics c "
                         "INNER JOIN(SELECT `group` FROM relationusersgroups a "
                         "INNER JOIN `groups` b ON a.group = b.id WHERE USER = '{}') d "
                         "ON c.id = d.`group`").format(userId)
                cursor_dbgroups.execute(query)
                result_set = cursor_dbgroups.fetchall()
                if not result_set:
                    raise EmptyDbException("No groups found")
                for row in result_set:
                    topic = row_to_topic(row)
                    topics_list.append(topic)
            connection_dbgroups.close()
            return topics_list
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def get_user_remaining_groups(cls, userId: int) -> list[Group]:
        try:
            connection_dbgroups = get_connection('dbgroups')
            groups_list = []
            with connection_dbgroups.cursor() as cursor_dbgroups:
                query = ("SELECT c.id, c.NAME, c.DESCRIPTION, c.class FROM `groups` c "
                         "LEFT JOIN(SELECT id, NAME, DESCRIPTION, class FROM relationusersgroups a "
                         "INNER JOIN `groups` b ON a.group = b.id WHERE USER = '{}') "
                         "d ON c.id = d.id WHERE d.id IS NULL").format(userId)
                cursor_dbgroups.execute(query)
                result_set = cursor_dbgroups.fetchall()
                if not result_set:
                    raise EmptyDbException("No groups found")
                for row in result_set:
                    group = row_to_group(row)
                    groups_list.append(group)
            connection_dbgroups.close()
            return groups_list
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
                         "email = '{}', image = '{}'").format(
                    user.username,
                    generate_password_hash(user.password),
                    user.name,
                    user.surname,
                    user.email,
                    user.image
                )
                cursor_dbusers.execute(query)
                connection_dbusers.commit()
                # Obtenemos la id creada por la bbdd para devolverla
                query = "select * from users where username = '{}'".format(user.username)
                cursor_dbusers.execute(query)
                user.id = cursor_dbusers.fetchone()[0]

            connection_dbusers.close()
            return user
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
    def delete_user_role(cls, userId: int, roleId: int):
        try:
            connection_dbusers = get_connection('dbusers')
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = "delete from relationusersroles where role = '{}' and user = '{}'".format(roleId, userId)
                cursor_dbusers.execute(query)
                connection_dbusers.commit()
            connection_dbusers.close()
            return f'Role {roleId} from User {userId} has been deleted'
        except NotFoundException:
            raise
        except Exception as ex:
            Logger.add_to_log("error", str(ex))
            Logger.add_to_log("error", traceback.format_exc())
            raise

    @classmethod
    def delete_user_group(cls, userId: int, groupId: int):
        try:
            connection_dbgroups = get_connection('dbgroups')
            with (connection_dbgroups.cursor()) as cursor_dbgroups:
                query = "delete from relationusersgroups where `group` = '{}' and user = '{}'".format(groupId, userId)
                cursor_dbgroups.execute(query)
                connection_dbgroups.commit()
            connection_dbgroups.close()
            return f'Group {groupId} from User {userId} has been deleted'
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
                query = ("update users set username = '{}', name = '{}' ,surname = '{}', email = '{}', image = '{}'"
                         "where id = '{}'").format(
                    user.username,
                    user.name,
                    user.surname,
                    user.email,
                    user.image,
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
    def update_password(cls, password, user_id):
        try:
            connection_dbusers = get_connection('dbusers')
            with (connection_dbusers.cursor()) as cursor_dbusers:
                query = "update users set password = '{}' where id = '{}'".format(generate_password_hash(password), user_id)
                cursor_dbusers.execute(query)
                connection_dbusers.commit()
            connection_dbusers.close()
            return f'User Password updated'
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
