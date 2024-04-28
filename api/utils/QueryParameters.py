class QueryParameters:

    def __init__(self, request):
        self.id = request.args.get("ids")
        self.username = request.args.get("username")
        self.name = request.args.get("name")
        self.email = request.args.get("email")
        self.permissionType = request.args.get("type")

    def add_to_query(self, query: str):
        for param in self.__dict__:
            param_value = getattr(self, param)
            if param_value is not None:
                if "where" not in query:
                    query += f" where `{param}` in {self.parseParam(param, param_value)}"
                else:
                    query += f" and `{param}` in {self.parseParam(param, param_value)}"
        return query

    def parseParam(self, param, value):
        if param == "id":
            id_list = self.id.split(',')
            if len(id_list) == 1:
                return f"('{id_list[0]}')"
            else:
                return tuple(self.id.split(','))
        else:
            return f"('{value}')"
