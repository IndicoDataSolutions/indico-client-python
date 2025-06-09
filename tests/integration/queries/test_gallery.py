import pytest

from indico.client import IndicoClient
from indico.queries.gallery import GetGalleryTags, ListGallery
from indico.types.component_blueprint import BlueprintPage, BlueprintTags


def test_list_gallery(indico):
    """Test listing all blueprints from the gallery."""
    client = IndicoClient()

    bppage = client.call(ListGallery())
    assert isinstance(bppage, BlueprintPage)
    assert hasattr(bppage, "blueprints")

    if bppage.blueprints:
        blueprint = bppage.blueprints[0]
        assert hasattr(blueprint, "id")
        assert hasattr(blueprint, "name")
        assert hasattr(blueprint, "component_type")
        assert hasattr(blueprint, "icon")
        assert hasattr(blueprint, "description")
        assert hasattr(blueprint, "enabled")
        assert hasattr(blueprint, "footer")
        assert hasattr(blueprint, "tags")
        assert hasattr(blueprint, "model_options")


def test_list_gallery_with_args(indico):
    """Test listing gallery blueprints with variables."""
    client = IndicoClient()

    limit_bppage = client.call(ListGallery(limit=5))
    assert isinstance(limit_bppage, BlueprintPage)
    assert len(limit_bppage.blueprints) <= 5

    desc_bppage = client.call(ListGallery(order_by="name", desc=True))
    assert isinstance(desc_bppage, BlueprintPage)

    filters = {
        "op": "and",
        "filters": [
            {
                "op": "eq",
                "field": "component_type",
                "value": "model_group",
            }
        ],
    }
    filtered_bppage = client.call(ListGallery(filters=filters))
    assert isinstance(filtered_bppage, BlueprintPage)
    filtered_component_bps = filtered_bppage.blueprints
    assert filtered_component_bps[0].component_type == "MODEL_GROUP"
    assert filtered_component_bps[-1].component_type == "MODEL_GROUP"


def test_list_gallery_pagination(indico):
    """Test gallery pagination functionality using the new cursor-based pagination."""
    client = IndicoClient()
    blueprints = []
    num_pages_to_check = 3  # Check 3 pages of results

    # Use paginate to get multiple pages
    for i, page in enumerate(client.paginate(ListGallery(limit=2))):
        assert isinstance(page, BlueprintPage)
        assert len(page.blueprints) <= 2
        blueprints.extend(page.blueprints)

        if i >= num_pages_to_check - 1:
            break

    # Verify we got results
    assert blueprints is not None
    assert len(blueprints) > 0

    # Verify we got different results on each page
    if len(blueprints) >= 2:
        # Check that we have unique blueprints
        blueprint_ids = [bp.id for bp in blueprints]
        assert len(blueprint_ids) == len(
            set(blueprint_ids)
        ), "Duplicate blueprints found in pagination"


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
        assert hasattr(tag, "tag_category")


def test_get_gallery_tags_with_args(indico):
    """Test retrieving gallery tags with filters."""
    client = IndicoClient()

    # Test with component family filter
    tags = client.call(GetGalleryTags(component_family="MODEL"))
    assert isinstance(tags, BlueprintTags)

    # Test with tag categories filter
    tags = client.call(GetGalleryTags(tag_categories=["PROVIDER"]))
    assert isinstance(tags, BlueprintTags)

    # Test with both filters
    tags = client.call(
        GetGalleryTags(component_family="MODEL", tag_categories=["PROVIDER"])
    )
    assert isinstance(tags, BlueprintTags)
