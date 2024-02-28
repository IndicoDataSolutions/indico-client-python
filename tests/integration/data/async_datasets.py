import pytest_asyncio
import time
from pathlib import Path
from indico.client import AsyncIndicoClient
from indico.queries import (
    CreateDataset,
)


@pytest_asyncio.fixture(scope="module")
async def aio_org_annotate_dataset(indico):
    dataset_filepath = str(Path(__file__).parents[0]) + "/org-annotate-labeled.csv"
    async with AsyncIndicoClient() as client:
        response = await client.call(
            CreateDataset(
                name=f"OrgAnnotate-test-{int(time.time())}", files=[dataset_filepath]
            )
        )
    assert response.status == "COMPLETE"
    return response
