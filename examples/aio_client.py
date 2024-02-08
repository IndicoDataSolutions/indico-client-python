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

config = IndicoConfig(host="app.indico.io")

async def example_with_client():
    """
    RECOMMENDED: use the client context manager to handle creation
    and cleanup
    """
    async with AsyncIndicoClient(config=config) as client:
        print(await client.get_ipa_version())
        await example_1(client)


async def example_basic_client():
    """Manage creation and cleanup of the client yourself"""

    # The .create() is required!
    client = await AsyncIndicoClient(config=config).create()

    # Note this is the equivalent to calling
    #   client = AsyncIndicoClient(config=config)
    #   await client.create()

    print(await client.get_ipa_version())
    await example_1(client)

    await client.cleanup()

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
            client.call(
                CreateDataset(name=f"My Dataset {i}", files=[filename])
            )
            for i in range(1, 4)
        )
    )
    assert len(datasets) == 3
    assert all(ds.status == 'COMPLETED' for ds in datasets)



if __name__ == "__main__":
    # How to run a Python script using async
    asyncio.run(example_with_client)
