

class Subject:

    def __init__(self, subjectId, code, title, course):
        self.subjectId = subjectId
        self.code = code
        self.title = title
        self.course = course

    def to_json(self):
        return {
            'id': self.subjectId,
            'code': self.code,
            'title': self.title,
            'course': self.course
        }


def row_to_subject(row):
    return Subject(
        subjectId=row[0],
        code=row[1],
        title=row[2],
        course=row[3],
    )
