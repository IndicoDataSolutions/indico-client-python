"""
The async client can be used as a replacement for the synchronous
IndicoClient to make concurrent calls to the platform
"""

import asyncio
from indico import AsyncIndicoClient, IndicoConfig
from indico.queries import CreateDataset


"""
Examples for client creation
"""

config = IndicoConfig(host="try.indico.io")


async def example_with_client():
    """
    Use the client context manager to handle creation
    and cleanup
    """
    async with AsyncIndicoClient(config=config) as client:
        print(await client.get_ipa_version())
        await example_1(client)


"""
Examples of fun async usage
"""


async def example_1(client):
    """
    Use an async client to create 3 datasets concurrently
    """
    filename = "my_file_for_all_datasets.pdf"
    datasets = await asyncio.gather(
        *(
            client.call(CreateDataset(name=f"My Dataset {i}", files=[filename]))
            for i in range(1, 4)
        )
    )
    assert len(datasets) == 3
    assert all(ds.status == "COMPLETED" for ds in datasets)


if __name__ == "__main__":
    # How to run a Python script using async
    asyncio.run(example_with_client())
