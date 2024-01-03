from .query import Query, QueryResults
from .exceptions import GreffErrorResponseException


class HTTPClient:
    def request(self, query: str) -> dict:
        raise NotImplementedError

    def query(self, query: str | Query) -> QueryResults:
        if not isinstance(query, (str, Query)):
            query = Query(query).serialize()
        elif isinstance(query, Query):
            query = query.serialize()

        raw_response = self.request(query)
        errors = raw_response.get("errors")

        if errors:
            raise GreffErrorResponseException(errors)
        return QueryResults(raw_response)
