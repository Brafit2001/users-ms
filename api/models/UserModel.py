class User:

    def __init__(self, userId, username, password, name, surname, image, email) -> None:
        self.id = userId
        self.username = username
        self.password = password
        self.surname = surname
        self.name = name
        self.email = email
        self.image = image

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'surname': self.surname,
            'name': self.name,
            'email': self.email,
            'image': self.image
        }


def row_to_user(row):
    return User(
        userId=row[0],
        username=row[1],
        password=row[2],
        name=row[3],
        surname=row[4],
        email=row[5],
        image=row[6])
