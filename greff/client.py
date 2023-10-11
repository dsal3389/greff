from typing import Callable, Iterable
from .exceptions import GraphqlResponseException
from .query import QueryRequest, QueryResponse
from .type import Type


class ClientProtocol:
    def query_request(self, query: str) -> dict:
        ...

    def mutate_request(self, mutate: str) -> dict:
        ...
    
    def query(
        self, 
        query: Iterable | str, 
        *, 
        fragments: dict | None = None, 
        root_types: Iterable[type[Type]] | None = None
    ) -> QueryResponse:
        query_request = QueryRequest(query=query, fragments=fragments)
        query_response = self.query_request(query_request.serialize())
        response_errros = query_response.get("errors")

        if response_errros is not None:
            raise GraphqlResponseException(response_errros)
        return QueryResponse(response=query_response)


class Client(ClientProtocol):
    def __init__(
        self,
        *,
        query_request: Callable[[str], dict] | None = None,
        mutate_request: Callable[[str], dict] | None = None
    ) -> None:
        self.query_request = query_request
        self.mutate_request = mutate_request
