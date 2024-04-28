from enum import Enum


class PermissionType(Enum):
    READ = 0
    WRITE = 1


class PermissionName(Enum):
    ROLES_MANAGER = 1
    USERS_MANAGER = 2
    COURSES_MANAGER = 3
    CLASSES_MANAGER = 4
    VOTES_MANAGER = 5
    GROUPS_MANAGER = 6
    TOPICS_MANAGER = 7


class Permission:

    def __init__(self, idPermission, permission_type: PermissionType):
        self.id = idPermission
        self.name = PermissionName(idPermission)
        self.permission_type = permission_type

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name.name,
            "type": self.permission_type.value
        }

    def to_tuple(self):
        return self.name, self.permission_type


def row_to_permission(row):
    return Permission(
        idPermission=row[0],
        permission_type=PermissionType(row[1])
    )
