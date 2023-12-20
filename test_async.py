import asyncio
import sys
import time
from indico.client.client import AsyncIndicoClient, IndicoClient
from indico.queries.datasets import ListDatasets
from indico.config import IndicoConfig

config = IndicoConfig(
    host="dev-ci.us-east-2.indico-dev.indico.io",
    api_token_path="/home/astha/Downloads/indico_api_token_devci.txt",
)


async def amain(limit, num_reqs):
    client = await AsyncIndicoClient(config=config).create()
    print(await client.get_ipa_version())
    await asyncio.gather(
        *(client.call(ListDatasets(limit=limit)) for i in range(num_reqs))
    )
    await client.cleanup()

def main(limit, num_reqs):
    client = IndicoClient(config=config)
    print(client.get_ipa_version())
    [
        client.call(ListDatasets(limit=limit)) for i in range(num_reqs)
    ]


if __name__ == "__main__":
    limit = 10
    num_reqs = 5
    print(f"Comparing async to sync with {limit=} {num_reqs=}")
    start = time.time()
    asyncio.run(amain(limit, num_reqs))
    print(f"async time {time.time() - start}")
    start = time.time()
    main(limit, num_reqs)
    print(f"sync time {time.time() - start}")
