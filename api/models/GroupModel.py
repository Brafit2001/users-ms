
class Group:

    def __init__(self, groupId, name, description, classId):
        self.groupId = groupId
        self.name = name
        self.description = description
        self.classId = classId

    def to_json(self):
        return {
            'id': self.groupId,
            'name': self.name,
            'description': self.description,
            'class': self.classId
        }


def row_to_group(row):
    return Group(
        groupId=row[0],
        name=row[1],
        description=row[2],
        classId=row[3]
    )
