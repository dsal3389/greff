from __future__ import annotations
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .query import QueryOP


class GraphqlError(TypedDict):
    message: str
    locations: list[dict[str, int]]


class QueryOperationException(Exception):
    def __init__(self, op: QueryOP, allowed_ops: list[QueryOP]) -> None:
        super().__init__(
            f"operation `{op}` is not allowed in this context, allowed only {', '.join(allowed_ops)}"
        )


class InvalidQueryException(Exception):
    pass


class TypenameConflictException(Exception):
    def __init__(self, typename: str) -> None:
        super().__init__(
            f"multiple graphql types found with the same typename `{typename}`"
        )


class GraphqlResponseException(Exception):
    def __init__(self, errors: list[GraphqlError]) -> None:
        self.errors = errors

        error_messages_str = ""
        for error_message in errors:
            error_messages_str += ("   * " + error_message.get('message') + "\n")
        super().__init__(f"graphql returned errors:\n{error_messages_str}")
