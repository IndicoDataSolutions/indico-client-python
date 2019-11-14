def test_list_model_groups(indico):
    results = indico.model_groups()
    assert isinstance(results, list)

    for result in results:
        assert "id" in result
        assert "name" in result
