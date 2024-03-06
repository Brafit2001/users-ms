class Instagram:

    def __init__(self, clipclassUser, instagramUser, password=None, session=None):
        self.clipclassUser = clipclassUser
        self.session = session
        self.instagramUser = instagramUser
        self.password = password

    def to_json(self):
        return {
            'clipclassUser': self.clipclassUser,
            'instagramUser': self.instagramUser,
            'session': self.session
        }
