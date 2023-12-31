from __future__ import annotations
from collections import namedtuple
from typing import ClassVar, Callable, NamedTuple
from pydantic import BaseModel, ConfigDict, field_validator

from .registry import registry
from .field import GreffModelField
from .types import GreffUndefined 


class Model(BaseModel):
    __typename__: ClassVar[str] = ""
    __implements__: ClassVar[dict[str, Model]] = {}
    __graphql_model_fields__: ClassVar[dict[str, GreffModelField]] = {}

    query: ClassVar[NamedTuple]
    model_config = ConfigDict(
        revalidate_instances="subclass-instances"
    )


def define_type(
    queryname: str = "",
    mutatename: str = "",
    typename: str = ""
) -> Callable[..., type[Model]]:
    def _define_type_deco(model: type[Model]) -> type[Model]:
        if not issubclass(model, Model):
            raise TypeError(
                f"`define_type` cannot run on classes that does not implement from `greff.Model`"
            )

        model.__queryname__ = queryname
        model.__mutatename__ = mutatename

        if typename:
            model.__typename__ = typename
        else:
            model.__typename__ = model.__name__.title()

        for parent in model.__mro__[1:]:
            if hasattr(parent, "__implements__"):
                parent.__implements__[model.__typename__] = model

        graphql_query_fields = {}
        for field_name, pydantic_field_info in model.model_fields.items():
            graphql_query_fields[field_name] = GreffModelField(field_name, model, pydantic_field_info)

        _model_query = namedtuple(f"{model.__name__}Query", graphql_query_fields.keys())
        model.query = _model_query(**graphql_query_fields)
        registry.register_model(model)
        return model
    return _define_type_deco
