import pytest
from indico.client import IndicoClient
from indico.filters import or_, UserSnapshotFilter
from indico.types.user_metrics import UserSummary
from indico.queries.usermetrics import GetUserSummary, GetUserSnapshots
from datetime import datetime


def test_fetch_summary(indico):
    client = IndicoClient()
    user_summary: UserSummary = client.call(GetUserSummary())
    assert user_summary is not None
    assert len(user_summary.app_roles) > 0


def test_fetch_snapshots(indico):
    client = IndicoClient()
    snapshots = []
    for snapshot in client.paginate(GetUserSnapshots(date=datetime.now())):
        snapshots.extend(snapshot)
    assert snapshots is not None
    assert snapshots[0] is not None
    assert len(snapshots) > 0
    first = snapshots.pop()
    assert first is not None
    assert first.roles is not None


def test_fetch_filtered_snapshots(indico):
    client = IndicoClient()
    snapshots = []
    filter_opts = or_(UserSnapshotFilter(user_id=1), UserSnapshotFilter(user_id=2))
    for snapshot in client.paginate(GetUserSnapshots(date=datetime.now(), filters=filter_opts)):
        snapshots.extend(snapshot)
    assert len(snapshots) == 2
