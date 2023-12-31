from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import Model


class GreffUnknownTypenameException(Exception):
    def __init__(self, model: type[Model], typename: str) -> None:
        super().__init__(f"graphql returned unknown typename `{typename}` for model `{model.__name__}`")
