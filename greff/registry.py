from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .model import Model


class _GreffModelRegistry:
    def __init__(self) -> None:
        self._registered_models = {}

    def register_model(self, model: type[Model]) -> None:
        self._registered_models[model.__typename__] = model
        if model.__queryname__:
            self._registered_models[model.__queryname__] = model

    def get_model(self, key: str) -> Optional[type[Model]]:
        return self._registered_models.get(key)


model_registry = _GreffModelRegistry()
