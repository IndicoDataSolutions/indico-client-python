import json
from datetime import datetime
from typing import TYPE_CHECKING, Any, cast, final

from pydantic import (
    AliasGenerator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    field_validator,
)
from pydantic.alias_generators import to_camel
from typing_extensions import Annotated

if TYPE_CHECKING:  # pragma: no cover
    from pydantic import ValidationInfo


class BaseType(BaseModel):
    model_config = ConfigDict(
        # alias fields so that they can be provided using their GraphQL
        # field names (camel case) or by their python names (snake case)
        alias_generator=AliasGenerator(validation_alias=to_camel),
        populate_by_name=True,
    )

    @field_validator("*", mode="before")
    @classmethod
    @final
    def _validate_legacy_datetime(cls, v: Any, info: "ValidationInfo") -> Any:
        # pydantic forces a UTC timezone when validating datetimes provided in epoch
        # time. this isn't backwards compat, so we override the built-in validation for
        # all fields defined with a datetime annotation with our legacy parsing
        if cls.model_fields[cast(str, info.field_name)].annotation == datetime:
            try:
                v = datetime.fromtimestamp(float(v))
            except ValueError:
                v = datetime.fromisoformat(v)

        return v


# this really should be dict[str, Any], but that breaks static typing since we'd supply
# the field as a string but the model's type would be annotated as a dict
JSONType = Annotated[Any, BeforeValidator(json.loads)]
