from __future__ import annotations
from collections import namedtuple
from typing import ClassVar, Callable, NamedTuple
from pydantic import BaseModel, ConfigDict

from .registry import model_registry
from .field import GreffModelField


class ModelTemplate(BaseModel):
    """
    ```py
        import greff
        from typing import TypeVar, Generic

        T = TypeVar("T")


        class ListTemplate(greff.Model, Generic[T]):
            values: list[T]
            count: int


        @greff.define_type()
        class Item(greff.Model):
            name: str


        @greff.define_type()
        class ListItem(ListTemplate[Item]):
            pass
    ```

    """

    pass


class Model(BaseModel):
    """
    the model class provides typing validations (with pydantic) and
    other required attributes that are used accross the `greff` library.

    ```py
        import greff

        class GraphqlEntry(greff.Model):
            ...
    ```

    as said before, this class only provide the basic needs, but it doesn't define a graphlq
    type that can be queried from the graphql api, for that we need `greff.define_type`.
    """

    __typename__: ClassVar[str] = ""
    __implements__: ClassVar[dict[str, Model]] = {}

    query: ClassVar[NamedTuple]
    model_config = ConfigDict(revalidate_instances="subclass-instances")


def define_type(
    queryname: str = "", mutatename: str = "", typename: str = ""
) -> Callable[..., type[Model]]:
    """
    model decorator that defines the given model as a graphql entry type that
    we can query / mutate
    """

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
            if issubclass(parent, Model):
                parent.__implements__[model.__typename__] = model

        graphql_query_fields = {}
        for field_name, pydantic_field_info in model.model_fields.items():
            graphql_query_fields[field_name] = GreffModelField(
                field_name, model, pydantic_field_info
            )

        model_query_nt = namedtuple(
            f"{model.__name__}Query", graphql_query_fields.keys()
        )
        model.query = model_query_nt(**graphql_query_fields)
        model_registry.register_model(model)
        return model

    return _define_type_deco


def implements(models: list[type[Model]]):
    """
    a decorator that is used on models to explicity define
    what those models implement, this is useful for subfields that
    can implement many different types, but those types are not inhertied
    by the model, for example

    @greff.define_type()
    class Host(greff.Model):
        ...


    @greff.define_type()
    class Group(greff.Model):
        ...


    @implements((
        Host,
        Group
    ))
    class NetworkObjects(greff.Model):
        pass
    """

    def _implements_wrapper(implementer: type[Model]) -> type[Model]:
        for model in models:
            if not issubclass(model, Model):
                raise TypeError(
                    f"function `implements` accept a list of class that inherit from `greff.Model`, "
                    "but got `{model.__name__}`"
                )
            implementer.__implements__[model.__typename__] = model

    return _implements_wrapper
