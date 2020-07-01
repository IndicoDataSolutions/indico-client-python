from indico.types.utils import cc_to_snake, snake_to_cc


def test_cc_to_snake():
    assert cc_to_snake("selectedModel") == "selected_model"

def test_snake_to_cc():
    assert snake_to_cc("selected_model") == "selectedModel"
    assert snake_to_cc("_selected_model") == "SelectedModel"
    assert snake_to_cc("_selected_model_") == "SelectedModel_"
