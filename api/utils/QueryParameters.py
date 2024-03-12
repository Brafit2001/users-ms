class QueryParameters:

    def __init__(self, request):
        self.username = request.args.get("username")
        self.name = request.args.get("name")
        self.email = request.args.get("email")

    def add_to_query(self, query: str):
        for param in self.__dict__:
            param_value = getattr(self, param)
            if param_value is not None:

                if "where" not in query:
                    query += f" where `{param}` in ('{param_value}')"
                else:
                    query += f" and `{param}` in ('{param_value}')"
        return query
