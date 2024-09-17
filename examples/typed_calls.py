"""
The async client can be used as a replacement for the synchronous
IndicoClient to make concurrent calls to the platform
"""

import asyncio
from typing import AsyncIterator, List

from indico import AsyncIndicoClient, IndicoConfig
from indico.queries import CreateDataset
from indico.queries.datasets import GetDataset, ListDatasets
from indico.types.dataset import Dataset
from indico.types.submission import Submission

"""
Example illustrating how to use the client in typed contexts
"""

config = IndicoConfig(host="try.indico.io")


async def main():
    async with AsyncIndicoClient(config=config) as client:
        ipa_version: str = await client.get_ipa_version()
        print(ipa_version)

        filename: str = "my_file_for_all_datasets.pdf"

        # CreateDataset is typed to return a Dataset, so multiple concurrent calls
        # via asyncio.gather should, and does, return List[Dataset]
        datasets: List[Dataset] = await asyncio.gather(
            *(
                client.call(CreateDataset(name=f"My Dataset {i}", files=[filename]))
                for i in range(1, 4)
            )
        )
        assert len(datasets) == 3

        # paginated calls are also properly typed
        pages: AsyncIterator[List[Dataset]] = client.paginate(ListDatasets())
        async for datasets in pages:
            for d in datasets:
                print(d.id)

        # incorrect typing will throw mypy / ide linting errors when using those tools.
        # here, Pyright correctly reports '"Dataset" is not the same as "Submission"'
        not_a_submission: Submission = await client.call(GetDataset(datasets[0].id))


if __name__ == "__main__":
    # How to run a Python script using async
    asyncio.run(main())
