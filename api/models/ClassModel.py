
class ClassModel:

    def __init__(self, classId,subject, title, image):
        self.classId = classId
        self.subject = subject
        self.title = title
        self.image = image

    def to_json(self):
        return {
            'id': self.classId,
            'subject': self.subject,
            'title': self.title,
            'image': self.image,
        }


def row_to_class_model(row):
    return ClassModel(
        classId=row[0],
        subject=row[1],
        title=row[2],
        image=row[3]
    )
