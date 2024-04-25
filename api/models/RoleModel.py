
class Role:
    def __init__(self, idRole, name) -> None:
        self.id = idRole
        self.name = name

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name
        }


def row_to_role(row) -> Role:
    return Role(
        idRole=row[0],
        name=row[1]
    )
