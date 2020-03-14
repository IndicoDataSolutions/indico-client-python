from indico.types.utils import cc_to_snake


def test_cc_to_snake():
    assert cc_to_snake("selectedModel") == "selected_model"
