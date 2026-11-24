# Indico IPA platform Client

### A python client library for the [Indico IPA Platform](https://try.indico.io/).

### See the full [Documentation](https://indicodatasolutions.github.io/indico-client-python/).

# Installation

---

Required: Python 3.9+

From PyPI:

```bash
pip3 install indico-client
```

From source:

Using UV (recommended):

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

git clone https://github.com/IndicoDataSolutions/indico-client-python.git
cd indico-client-python
uv pip install -e ".[all]"
```

Or using pip:

```bash
git clone https://github.com/IndicoDataSolutions/indico-client-python.git
cd indico-client-python
pip install -e ".[all]"
```

Running in a Docker container:

```
docker build -t indico-client .
docker run -it indico-client bash
```

# Getting Started

## Authentication

### Indico API token

The Indico Platform and Client Libraries use JSON Web Tokens (JWT) for user
authentication. Details on acquiring this token can be found at this [documentation](https://docs.indicodata.ai/articles/#!common-questions-publication/how-do-i-get-started-developing-with-the-indico-api/q/API%2520token/qid/3328/qp/1)

### Environment variables

The following environment variables are used for authentication in the default `IndicoClient` object

- `INDICO_HOST`: URL of the IPA instance
- `INDICO_API_TOKEN`: user token downloaded from these [directions](#indico-api-token)

## API Examples

### Creating a Client

```python3
from indico import IndicoClient, IndicoConfig

config = IndicoConfig(
    host='try.indico.io', # or your custom app location
    api_token_path='./indico_api_token.txt' # path to your API token
    )
client = IndicoClient(config=config)
```

### Pure GraphQL example

```
from indico import IndicoClient
from indico.client.request import GraphQLRequest

client = IndicoClient()
response = client.call(GraphQLRequest(
    query="""
        query modelGroupQueries($ids: [Int]) {
	        modelGroups(modelGroupIds: $ids){
                modelGroups{
                    id
                }
            }
        }
    """,
    variables={"ids": [1]}
))

model_groups = response["model_groups"]["model_groups"]
```

# Testing the SDK

To run the tests associated with this repo perform the following:

### Prerequisite

Ensure you have set the environment variables detailed [here](#environment-variables)

You will also need the following env variables set for the Exchange integration tests:

- `EXCH_TENANT_ID`
- `EXCH_CLIENT_ID`
- `EXCH_CLIENT_SECRET`
- `EXCH_USER_ID`

### Running the tests

Using UV (recommended):

1. Install UV if you haven't already
   `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Install the client and test dependencies
   `uv pip install -e ".[all]" "pytest<8" "requests-mock>=1.8.0" "pytest-asyncio>0.21"`
3. Run tests
   `pytest -sv --host <indico_host> tests/`
   _ Only run unit tests `pytest -sv --host <indico_host> tests/unit/`
   _ Only run integration tests `pytest -sv --host <indico_host> tests/integration/`
4. Check typing
   ```sh
   uv pip install "mypy==1.8" typing_extensions pandas-stubs types-requests types-pytz types-openpyxl
   mypy --config-file=pyproject.toml
   ```

Or using pip:

1. Create a virtual environment
   `python3 -m venv venv`
2. Activate the virtual environment
   `source venv/bin/activate`
3. Install the client
   `pip3 install --editable .[all]`
4. Install test deps
   `pip3 install "pytest<8" "requests-mock>=1.8.0" "pytest-asyncio>0.21"`
5. Run tests
   `pytest -sv --host <indico_host> tests/`
   _ Only run unit tests `pytest -sv --host <indico_host> tests/unit/`
   _ Only run integration tests `pytest -sv --host <indico_host> tests/integration/`
6. Check typing
   ```sh
   pip3 install "mypy==1.8" typing_extensions pandas-stubs types-requests types-pytz types-openpyxl
   mypy --config-file=pyproject.toml
   ```

Alternatively, run all the unit tests via `docker compose run --rm tester`

# Releasing

Pushing a version tag runs `.github/workflows/release.yml`. It runs the tests, builds, checks the built version equals the tag, waits for approval, publishes to PyPI through trusted publishing, and creates a GitHub Release with generated notes. Alpha, beta, rc and dev tags are marked as pre-releases.

### Release with the script

```sh
# Check everything without tagging or pushing
scripts/release.sh 7.11.0 --dry-run
# Tag HEAD and push the tag, after a confirmation prompt
scripts/release.sh 7.11.0
# Skip the confirmation prompt (required when not run from a terminal)
scripts/release.sh 7.11.0 --yes
# Allow a version below the highest X.Y.Z tagged on origin
scripts/release.sh 7.10.1 --allow-older
```

Manual equivalent:

```sh
git tag 7.11.0
git push origin refs/tags/7.11.0
```

### Tag rules

- No `v` prefix, lowercase, no leading zeros. Accepted shapes:
  - `7.11.0` release
  - `7.11.0-alpha1` publishes as `7.11.0a1`
  - `7.11.0-beta1` publishes as `7.11.0b1`
  - `7.11.0-rc1` publishes as `7.11.0rc1`
  - `7.11.0-a1` publishes as `7.11.0a1`
  - `7.11.0-b1` publishes as `7.11.0b1`
  - `7.11.0.post1` post release
  - `7.11.0.dev1` dev release
- The script refuses a version whose `X.Y.Z` is below the highest `X.Y.Z` already tagged on origin. `--allow-older` overrides this.
- A `.postN` release needs its base version tag (`7.11.0` for `7.11.0.post1`) to exist on origin.
- A version already published under another spelling is refused (`7.11.0-a1` when `7.11.0-alpha1` exists).
- Tag the exact commit to release. It must already be on origin; it need not be the tip of master.
- One tag per commit.
- Push one tag at a time, never `git push --tags`.
- A PyPI version cannot be reused.

### Approval

- Two teams own releases. Their members push version tags and approve publishing:
  - QA: `qa@indicodata.ai`, GitHub team `qa-indicodata-ai`
  - Intake: `intake@indicodata.ai`, GitHub team `intake-indicodata-ai`
- This is a deployment approval on the `pypi` environment, not a pull request review.
- After the tests and build pass, the publish job pauses. A member of either team opens the workflow run in the Actions tab and chooses "Review deployments".
- The approver confirms the tag is on the intended commit and the version is right.
- If the environment has "Prevent self-review" on, the approver must be someone other than the person who pushed the tag.

### If it fails

- Before upload nothing is published. Cancel the workflow run first if it is still running or waiting for approval, because deleting the tag does not cancel it. Then delete the tag and tag again:

```sh
git tag -d 7.11.0
git push origin :refs/tags/7.11.0
```

- At upload, re-run the failed job.
- If only the GitHub Release job fails, the package is already on PyPI. Re-run that job; do not delete the tag.
- If the re-run fails with "File already exists", part of the release is already on PyPI. Publish a `.postN` release instead.

# Contributing

This repository adheres (as best as possible) to the following standards:

- Python formatting with `ruff format`
  - Line Width=88
- [Google Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
