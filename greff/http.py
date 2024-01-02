from .query import Query, QueryResults


class HTTPClient:
    def request(self, query: str) -> dict:
        raise NotImplementedError

    def query(self, query: str | Query) -> QueryResults:
        if not isinstance(query, (str, Query)):
            query = Query(query).serialize()
        elif isinstance(query, Query):
            query = query.serialize()

        raw_response = self.request(query)
        return QueryResults(raw_response)
