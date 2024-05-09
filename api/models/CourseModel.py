
class Course:

    def __init__(self, courseId, title, year):
        self.id = courseId
        self.title = title
        self.year = year

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "year": self.year
        }


def row_to_course(row):
    return Course(
        courseId=row[0],
        title=row[1],
        year=row[2]
    )
