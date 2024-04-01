import pytest
from indico.client import IndicoClient
from indico.errors import IndicoInputError
from indico.queries.custom_blueprint import RegisterCustomBlueprint
from indico.types.workflow import ComponentFamily


def test_register_blueprint(indico):
    client = IndicoClient()
    bpreq = RegisterCustomBlueprint(
        component_family=ComponentFamily.OUTPUT, 
        name="Meowtput", 
        description="adds 'cat' to the result file", 
        config={
            "inputs": [{"name": "result_file", "ioClass": "PartitionStream"}],
            "outputs": [{"name": "result_file", "ioClass": "PartitionStream"}],
            "submissionLauncher": {"service": "customizer_default", "name": "cat_output"}
        },
        tags= ["custom"],
        all_access=True,
        footer="version 2"
    )
    bp = client.call(bpreq)
    print(bp.__dict__)
    assert bp.id

def test_register_blueprint_bad_config(indico):
    with pytest.raises(IndicoInputError):
        RegisterCustomBlueprint(
            component_family=ComponentFamily.OUTPUT, 
            name="Meowtput", 
            description="adds 'cat' to the result file", 
            config={
                "inputs": [{"name": "result_file", "ioClass": "PartitionStream"}],
                "outputs": [{"name": "result_file", "ioClass": "PartitionStream"}],
                "submissionLauncher": {}
            },
            tags= ["custom"],
            all_access=True,
            footer="version 2"
        )
