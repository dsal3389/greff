from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import Model


class GreffUnknownTypenameException(Exception):
    def __init__(self, model: type[Model], typename: str) -> None:
        super().__init__(
            f"graphql returned unknown typename `{typename}` for model `{model.__name__}`"
        )


class GreffErrorResponseException(Exception):
    def __init__(self, errors) -> None:
        self.errors = errors

        error_messages = []
        for error in self.errors:
            error_messages.append(error.get("message"))
        super().__init__("\n".join(error_messages))
