from __future__ import annotations

import enum
import inspect
import dataclasses
from typing import Any, Iterable

from .model import Model
from .registry import registry
from .field import GreffModelField
from .functions import implement_model_instance


class _GraphqlQueryOperationType(enum.Enum):
    ARGUMENTS = enum.auto()
    INLINE_FRAGMENT = enum.auto()
    FRAGMENT_REF = enum.auto()


_GreffQueryOperation = dataclasses.make_dataclass("_GreffQueryOperation", (
    ("op", _GraphqlQueryOperationType),
    ("model", Model | GreffModelField),
    ("extra", dict, dataclasses.field(default_factory=dict))
))


def arguments(
    model: Model | GreffModelField, 
    **kwargs
) -> _GreffQueryOperation:
    return _GreffQueryOperation(op=_GraphqlQueryOperationType.ARGUMENTS, model=model, extra=kwargs)


class Query:
    def __init__(self, query: Iterable[Iterable[Model, Iterable[GreffModelField]]]) -> None:
        self._query = query

    def serialize(self) -> str:
        return "".join(self._serialize())

    def _serialize(self) -> Iterable[str]:
        yield "query {"
        for types_query in self._query:
            yield from self._serialize_model_query(types_query, sub_field=False)
        yield "}"

    def _serialize_model_query(
        self, 
        model_query, 
        sub_field: bool = True
    ) -> Iterable[str]:
        model, fields = model_query

        if isinstance(model, _GreffQueryOperation):
            yield self._serialize_query_operation(model)
        else:
            if inspect.isclass(model) and issubclass(model, Model):
                if sub_field:
                    raise TypeError(
                        f"given query subfield a root model {model.__name__}"
                    )
            elif isinstance(model, GreffModelField):
                if not sub_field:
                    raise TypeError(
                        f"query provided a model from field for a root model `{model.model.__name__}.query.{model.name}`"
                    )
            yield model.__queryname__
        yield from self._serialize_fields_list(fields)

    def _serialize_fields_list(self, fields) -> Iterable[str]:
        first = True
        buf = "{"

        for field in fields:
            if first:
                first = False
            else:
                buf = ","

            if isinstance(field, (tuple, list, set, frozenset)):
                yield buf
                yield from self._serialize_model_query(field, sub_field=True)
            elif isinstance(field, GreffModelField):
                yield buf + field.name
        yield ",__typename}"

    def _serialize_query_operation(self, operation: _GreffQueryOperation) -> str:
        if operation.op is _GraphqlQueryOperationType.ARGUMENTS:
            serialized_arguments = ", ".join(f"{k}: \"{v}\"" for k,v in operation.extra.items())
            return f"{operation.model.__queryname__}({serialized_arguments})"


class QueryResults:
    def __init__(self, data: dict[str, ...]) -> None:
        self._data = data

    @property
    def data(self) -> dict[str, ...]:
        return self._data

    def groups(self) -> tuple[Iterable[Model], ...]:
        graphql_data = self.data.get("data")
        groups = []

        for model_name, model_data in graphql_data.items():
            model_type = registry.get_model(model_name)
            groups.append(self._iter_model_instances(model_type, model_data))
        return tuple(groups)

    def _iter_model_instances(self, model: type[Model], data: list[dict] | dict) -> Iterable[Model]:
        if isinstance(data, (list, tuple, set, frozenset)):
            for instance_data in data:
                yield implement_model_instance(model, instance_data)
        else:
            yield implement_model_instance(model, data)
