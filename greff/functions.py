from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any

from .model import Model
from .exceptions import GreffUnknownTypenameException


def implement_model_instance(
    model_type: type[Model], graphql_instance_data: dict[str, Any]
) -> Model:
    if not inspect.isclass(model_type) or not issubclass(model_type, Model):
        raise ValueError(f"function `implement_model_instance` accept model type")

    __typename = graphql_instance_data.pop("__typename", None)

    if __typename is not None:
        if __typename not in model_type.__implements__:
            raise GreffUnknownTypenameException(model_type, __typename)
        model_type = model_type.__implements__.get(__typename)
    return model_type(**graphql_instance_data)
