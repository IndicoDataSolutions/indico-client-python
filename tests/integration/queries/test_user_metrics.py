import pytest
from indico.client import IndicoClient
from indico.filters import or_, UserMetricsFilter
from indico.queries import JobStatus, RetrieveStorageObject
from indico.types.user_metrics import UserSummary
from indico.queries.usermetrics import (
    GetUserSummary,
    GetUserSnapshots,
    GetUserChangelog,
    GenerateChangelogReport,
)
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


def test_fetch_snapshots_with_limit(indico):
    client = IndicoClient()
    snapshots = client.call(GetUserSnapshots(date=datetime.now(), limit=10))
    assert snapshots is not None
    assert snapshots[0] is not None
    assert len(snapshots) == 10
    first = snapshots.pop()
    assert first is not None
    assert first.roles is not None


def test_fetch_filtered_snapshots(indico):
    client = IndicoClient()
    snapshots = client.call(GetUserSnapshots(date=datetime.now(), limit=2))
    user_ids = [s.id for s in snapshots]
    filtered_snapshots = []
    filter_opts = or_(
        UserMetricsFilter(user_id=user_ids[0]), UserMetricsFilter(user_id=user_ids[1])
    )
    for snapshot in client.paginate(
        GetUserSnapshots(date=datetime.now(), filters=filter_opts)
    ):
        filtered_snapshots.extend(snapshot)
    assert len(filtered_snapshots) == 2


def test_changelog(indico):
    client = IndicoClient()
    changelogs = []
    for log in client.paginate(
        (
            GetUserChangelog(
                start_date=datetime.now(), end_date=datetime.now(), limit=100
            )
        )
    ):
        changelogs.extend(log)
    assert len(changelogs) > 0


def test_csv_changelog(indico):
    client = IndicoClient()
    changelogs = client.call(
        (GenerateChangelogReport(start_date=datetime.now(), end_date=datetime.now()))
    )
    assert changelogs is not None
    job = changelogs.job_id
    assert job is not None
    job = client.call(JobStatus(id=job, wait=True))
    assert job.status == "SUCCESS"
    assert job.ready is True
    result = client.call(RetrieveStorageObject(job.result))
    assert result is not None
