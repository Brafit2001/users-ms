from enum import Enum


class PermissionType(Enum):
    READ = 0
    WRITE = 1


class PermissionName(Enum):
    VERIFY = 1
    ROLES_MANAGER = 2
    USERS_MANAGER = 3
    COURSES_MANAGER = 4
    CLASSES_MANAGER = 5
    VOTES_MANAGER = 6
    GROUPS_MANAGER = 7
    TOPICS_MANAGER = 8


class Permission:

    def __init__(self, idPermission, permission_type: PermissionType):
        self.name = PermissionName(idPermission)
        self.permission_type = permission_type

    def to_tuple(self):
        return self.name, self.permission_type
