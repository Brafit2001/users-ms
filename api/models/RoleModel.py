
class Role:
    def __init__(self, idRole, name) -> None:
        self.id = idRole
        self.name = name

    def to_json(self) -> dict:
        return {
            "idRole": self.id,
            "name": self.name
        }
