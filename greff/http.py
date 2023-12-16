from .query import QuerySerializer, QueryResults


class HTTPClient:
    def request(self, query: str) -> dict:
        raise NotImplementedError

    def query(self, query) -> dict:
        query_str = QuerySerializer(query).serialize()
        raw_response = self.request(query_str)
        return QueryResults(raw_response)
