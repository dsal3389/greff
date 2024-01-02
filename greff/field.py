from __future__ import annotations
from typing import TYPE_CHECKING
from pydantic import Field

if TYPE_CHECKING:
    from pydantic.fields import FieldInfo
    from .model import Model


class GreffModelField:
    def __init__(
        self,
        name: str,
        parent_model: Model,
        pydantic_field_info: FieldInfo
    ) -> None:
        self.name = name
        self._parent_model = parent_model
        self._pydantic_field_info = pydantic_field_info

    @property
    def model(self) -> Model:
        return self._parent_model

    @property
    def __queryname__(self) -> str:
        return self._pydantic_field_info.json_schema_extra["queryname"] or self.name


def field(queryname: str = "", *args, **kwargs) -> Field:
    kwargs["json_schema_extra"] = {
        "queryname": queryname
    }
    return Field(*args, **kwargs)
