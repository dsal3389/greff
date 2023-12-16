from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .model import Model


class _GreffModelRegistry:
    def __init__(self) -> None:
        self._registered_models = {}
    
    def register_model(self, model: type[Model]) -> None:
        self._registered_models[model.__typename__] = model

    def get_model(self, typename: str) -> Optional[type[Model]]:
        return self._query_models.get(typename)


registry = _GreffModelRegistry()
