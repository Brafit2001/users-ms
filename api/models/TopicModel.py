class Topic:

    def __init__(self, topicId, title, deadline, unit):
        self.topicId = topicId
        self.title = title
        self.deadline = deadline
        self.unit = unit

    def to_json(self):
        return {
            'id': self.topicId,
            'title': self.title,
            'deadline': self.deadline,
            'unit': self.unit
        }


def row_to_topic(row):
    return Topic(
        topicId=row[0],
        title=row[1],
        deadline=row[2],
        unit=row[3]
    )
