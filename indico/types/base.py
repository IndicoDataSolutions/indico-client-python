import json
from typing import Any

from pydantic import AliasGenerator, BaseModel, BeforeValidator, ConfigDict
from pydantic.alias_generators import to_camel
from typing_extensions import Annotated


class BaseType(BaseModel):
    model_config = ConfigDict(
        # alias fields so that they can be provided using their GraphQL
        # field names (camel case) or by their python names (snake case)
        alias_generator=AliasGenerator(validation_alias=to_camel),
        populate_by_name=True,
    )


# this really should be dict[str, Any], but that breaks static typing since we supply
# the field as a string but the model's type would be annotated as a dict
JSONType = Annotated[Any, BeforeValidator(json.loads)]
