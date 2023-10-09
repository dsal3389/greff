from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .query import QueryOP


class GraphqlError(TypedDict):
    message: str
    locations: list[dict[str, int]]


class GraphqlErrorResponse(TypedDict):
    data: list
    errors: list[GraphqlError]


class QueryOperationException(Exception):
    def __init__(self, op: QueryOP, allowed_ops: list[QueryOP]) -> None:
        super().__init__(
            f"operation `{op}` is not allowed in this context, allowed only {', '.join(allowed_ops)}"
        )


class InvalidQueryException(Exception):
    pass


class GraphqlResponseException(Exception):
    def __init__(self, error_response: GraphqlErrorResponse) -> None:
        self.response = error_response

        error_messages_str = ""
        for error_message in error_response.get("errors", []):
            error_messages_str += ("   * " + error_message.get('message') + "\n")
        super().__init__(f"graphql returned errors:\n{error_messages_str}")
