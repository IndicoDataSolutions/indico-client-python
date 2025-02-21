from typing import Any, Dict, List, Optional

from indico.types.base import BaseType


class ComponentBlueprint(BaseType):
    id: int
    name: str
    component_type: str
    icon: str
    description: str
    enabled: bool
    footer: str
    tags: List[str]
    model_options: Dict[str, Any]

    @property
    def is_ootb(self) -> bool:
        """
        Check if the component blueprint is an out-of-the-box (OOTB) component.

        Returns:
            bool: True if the component blueprint is an OOTB component, False otherwise.
        """
        has_ootb = "ootb" in self.tags
        has_editable = "editable" in self.tags

        return has_ootb or has_editable


class BlueprintPage(BaseType):
    blueprints: List[ComponentBlueprint]

    def get_by_ctype(self, component_type: str) -> Optional[ComponentBlueprint]:
        """
        Get a blueprint by component type.
        """
        return next(
            (
                blueprint
                for blueprint in self.blueprints
                if blueprint.component_type == component_type
            ),
            None,
        )

    def get_by_tags(self, tags: List[str]) -> Optional[ComponentBlueprint]:
        """
        Get a blueprint by tags.
        """
        return next(
            (
                blueprint
                for blueprint in self.blueprints
                if set(tags) <= set(blueprint.tags)
            ),
            None,
        )


class Tag(BaseType):
    tag: str
    value: str


class BlueprintTags(BaseType):
    tags: List[Tag]

    def get_tag_by_value(self, value: str) -> Optional[Tag]:
        """
        Get a tag by value.
        """
        return next(
            (tag for tag in self.tags if tag.value == value),
            None,
        )

    def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """
        Get a tag by name.
        """
        return next(
            (tag for tag in self.tags if tag.tag == name),
            None,
        )
