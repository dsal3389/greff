from typing import Callable
from .query import Query


class ClientProtocol:
    def query_request(self, query: str) -> dict:
        ...

    def mutate_request(self, mutate: str) -> dict:
        ...

    def query(self, query, fragments = None) -> Query:
        return Query(client=self, query=query, fragments=fragments)


class Client(ClientProtocol):
    def __init__(
        self,
        *,
        query_request: Callable[[str], dict] | None = None,
        mutate_request: Callable[[str], dict] | None = None
    ) -> None:
        self.query_request = query_request
        self.mutate_request = mutate_request
