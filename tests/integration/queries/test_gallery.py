import pytest
from indico.client import IndicoClient
from indico.queries.gallery import ListGallery, GetGalleryTags
from indico.types.component_blueprint import BlueprintPage, BlueprintTags


def test_list_gallery(indico):
    """Test listing all blueprints from the gallery."""
    client = IndicoClient()

    # Test default listing
    blueprints = client.call(ListGallery())
    assert isinstance(blueprints, BlueprintPage)
    assert hasattr(blueprints, "blueprints")
    assert hasattr(blueprints, "cursor")
    assert hasattr(blueprints, "total")

    # Verify blueprint structure
    if blueprints.blueprints:
        blueprint = blueprints.blueprints[0]
        assert hasattr(blueprint, "id")
        assert hasattr(blueprint, "name")
        assert hasattr(blueprint, "componentType")
        assert hasattr(blueprint, "icon")
        assert hasattr(blueprint, "description")
        assert hasattr(blueprint, "enabled")
        assert hasattr(blueprint, "footer")
        assert hasattr(blueprint, "tags")
        assert hasattr(blueprint, "modelOptions")


def test_list_gallery_with_filters(indico):
    """Test listing gallery blueprints with filters."""
    client = IndicoClient()

    # Test with limit
    blueprints = client.call(ListGallery(limit=5))
    assert isinstance(blueprints, BlueprintPage)
    assert len(blueprints.blueprints) <= 5

    # Test with ordering
    blueprints_desc = client.call(ListGallery(order_by="ID", desc=True))
    blueprints_asc = client.call(ListGallery(order_by="ID", desc=False))
    assert isinstance(blueprints_desc, BlueprintPage)
    assert isinstance(blueprints_asc, BlueprintPage)


def test_list_gallery_pagination(indico):
    """Test gallery pagination functionality."""
    client = IndicoClient()

    # Get first page
    first_page = client.call(ListGallery(limit=2))
    assert isinstance(first_page, BlueprintPage)
    assert len(first_page.blueprints) <= 2

    # Get second page using cursor
    if first_page.cursor:
        second_page = client.call(ListGallery(limit=2, cursor=first_page.cursor))
        assert isinstance(second_page, BlueprintPage)
        assert len(second_page.blueprints) <= 2

        # Verify different results
        if first_page.blueprints and second_page.blueprints:
            assert first_page.blueprints[0].id != second_page.blueprints[0].id


def test_get_gallery_tags(indico):
    """Test retrieving gallery tags."""
    client = IndicoClient()

    # Test getting all tags
    tags = client.call(GetGalleryTags())
    assert isinstance(tags, BlueprintTags)
    assert hasattr(tags, "tags")

    # Verify tag structure
    if tags.tags:
        tag = tags.tags[0]
        assert hasattr(tag, "tag")
        assert hasattr(tag, "value")
        assert hasattr(tag, "tagCategory")


def test_get_gallery_tags_with_filters(indico):
    """Test retrieving gallery tags with filters."""
    client = IndicoClient()

    # Test with component family filter
    tags = client.call(GetGalleryTags(component_family="MODEL"))
    assert isinstance(tags, BlueprintTags)

    # Test with tag categories filter
    tags = client.call(GetGalleryTags(tag_categories=["CATEGORY"]))
    assert isinstance(tags, BlueprintTags)

    # Test with both filters
    tags = client.call(
        GetGalleryTags(component_family="MODEL", tag_categories=["CATEGORY"])
    )
    assert isinstance(tags, BlueprintTags)
