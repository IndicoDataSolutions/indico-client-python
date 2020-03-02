import pytest

PREDICTION_TEXT = "This is a test prediction. If a finetune model predicts on this we may get an empty list as result."


@pytest.fixture(scope="module")
def model_group(indico):
    results = indico.model_groups()
    try:
        return next(
            result
            for result in results
            if not result["retrainRequired"]
            and result["status"] == "COMPLETE"
            and result.get_selected_model().get("id")
        )
    except StopIteration:
        raise AssertionError(
            "The authenticated user does not have a successfully trained model"
        )


def test_model_group_predict(model_group):
    result = model_group.predict([PREDICTION_TEXT])

    # TODO: Break this test by task_type and have saved model groups for these tests. this will require a test user api token.
    assert isinstance(result, list)
    assert len(result) == 1


def test_model_group_info(model_group):
    result = model_group.info()

    assert isinstance(result, dict)
    assert "class_counts" in result
    assert "class_names" in result
    assert "metrics" in result


def test_model_group_load(model_group):

    """
    TODO: Ensure this test passes with Finetune model
    """
    result = model_group.load()
    assert result == "ready"


def test_model_group_predict_with_model_id(model_group):
    model_id = model_group.get_selected_model().get("id")
    result = model_group.predict([PREDICTION_TEXT], model_id=model_id)
    assert isinstance(result, list)
    assert len(result) == 1
