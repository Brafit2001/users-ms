def parseParam(param, value):
    if param == "id" or param == "avoid":
        id_list = value.split(',')
        if len(id_list) == 1:
            return f"('{id_list[0]}')"
        else:
            return tuple(value.split(','))
    else:
        return f"('{value}')"


class QueryParameters:

    def __init__(self, request):
        self.id = request.args.get("ids")
        self.username = request.args.get("username")
        self.name = request.args.get("name")
        self.email = request.args.get("email")
        self.permissionType = request.args.get("type")
        self.avoid = request.args.get("avoid")

    def add_to_query(self, query: str):
        for param in self.__dict__:
            param_value = getattr(self, param)
            if param_value is not None:
                if "where" not in query:
                    if param == "avoid":
                        query += f" where `id` not in {parseParam(param, param_value)}"
                    else:
                        query += f" where `{param}` in {parseParam(param, param_value)}"
                else:
                    if param == "avoid":
                        query += f" and `id` not in {parseParam(param, param_value)}"
                    else:
                        query += f" and `{param}` in {parseParam(param, param_value)}"
        return query
