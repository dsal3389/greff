from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .query import QueryOP


class QueryOperationException(Exception):
    def __init__(self, op: QueryOP, allowed_ops: list[QueryOP]) -> None:
        super().__init__(
            f"operation `{op}` is not allowed in this context, allowed only {', '.join(allowed_ops)}"
        )
