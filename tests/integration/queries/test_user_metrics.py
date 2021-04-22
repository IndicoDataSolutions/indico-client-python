from pathlib import Path

import pytest

from indico.client import IndicoClient
from indico.queries import JobStatus, DocumentExtraction
from indico.types.jobs import Job
from indico.errors import IndicoTimeoutError
from indico.types.user_metrics import UserSummary, UserSnapshots
from indico.queries.usermetrics import GetUserSummary, GetUserSnapshots
from datetime import datetime


def test_fetch_summary(indico):
    client = IndicoClient()
    userSummary = client.call(GetUserSummary())
    assert userSummary is not None
    assert len(userSummary.app_roles) > 0

def test_fetch_snapshots(indico):
    client = IndicoClient()
    snapshots: UserSnapshots = client.call(GetUserSnapshots(date=datetime.now(), user_id=195))
    print(snapshots)
    assert snapshots is not None
    assert snapshots.results is not None
    assert len(snapshots.results) > 0
    first = snapshots.results.pop()
    assert first is not None
    assert first.roles is not None

