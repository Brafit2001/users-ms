class User:

    def __init__(self, idUser, group, username, password, name, surname, image, email) -> None:
        self.id = idUser
        self.group = group
        self.username = username
        self.password = password
        self.surname = surname
        self.name = name
        self.email = email
        self.image = image

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'group': self.group,
            'username': self.username,
            'password': self.password,
            'surname': self.surname,
            'name': self.name,
            'email': self.email,
            'image': self.image
        }


class UserData:

    def __init__(self, idUser, group, username, name, surname, image, email) -> None:
        self.id = idUser
        self.group = group
        self.username = username
        self.surname = surname
        self.name = name
        self.email = email
        self.image = image

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'group': self.group,
            'username': self.username,
            'surname': self.surname,
            'name': self.name,
            'email': self.email,
            'image': self.image
        }


class UserCourse:

    def __init__(self, username, classId, course) -> None:
        self.user = username
        self.classId = classId
        self.course = course
