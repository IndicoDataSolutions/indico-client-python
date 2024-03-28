from datetime import datetime, timedelta

from indico import IndicoClient, IndicoConfig
from indico.filters import UserMetricsFilter, or_
from indico.queries import JobStatus, RetrieveStorageObject
from indico.queries.usermetrics import (
    GenerateChangelogReport,
    GetUserChangelog,
    GetUserSnapshots,
    GetUserSummary,
)
from indico.types.user_metrics import UserSummary

"""
Example 1: User Summary
"""
# Create an Indico API client
my_config = IndicoConfig(
    host="try.indico.io", api_token_path="./path/to/indico_api_token.txt"
)
client = IndicoClient(config=my_config)

user_summary: UserSummary = client.call(GetUserSummary())
print("Wow! there's " + str(user_summary.users.enabled) + " users enabled on the app!")
print(
    "Did you know there are "
    + str(len(user_summary.app_roles))
    + " roles available here?"
)

"""

Example 2: User Snapshots
Snapshots are paginated and iterable,
so you can continue to iterate over them to build a full set
"""
snapshots = []
for snapshot in client.paginate(GetUserSnapshots(date=datetime.now())):
    snapshots.extend(snapshot)

print("Fetched " + str(len(snapshots)) + " users for analysis")

"""

Example 3: Filtered User Snapshots
Filter by userid or email.

"""
snapshots = []
filter_opts = or_(UserMetricsFilter(user_id=1))
for snapshot in client.paginate(
    GetUserSnapshots(date=datetime.now(), filters=filter_opts)
):
    snapshots.extend(snapshot)
print("Fetched just " + str(len(snapshots)) + " user for analysis")

"""

Example 4: Fetching a UserChangeLogs by API
Pull in a limited set of user change data using the graph QL API
"""
# This is useful if you want only a limited selection of the changelogs
changelogs = []
for log in client.paginate(
    (GetUserChangelog(start_date=datetime.now(), end_date=datetime.now(), limit=100))
):
    changelogs.extend(log)
print("Fetched " + str(len(changelogs)) + " changes for the day")

"""
Example 5: Fetching longer User Change Logs as CSV
Use the GenerateChangelogReport to get a longer changelog as CSV (or json)
"""
# Set the start date and end date
start_date = datetime.today() - timedelta(days=7)
changelogs = client.call(
    (GenerateChangelogReport(start_date=start_date, end_date=datetime.now()))
)
# This generates a job which can be waited for
job_id = changelogs.job_id
job = client.call(JobStatus(id=job_id, wait=True))
# And the job will contain a storage object file with the full report.
result = client.call(RetrieveStorageObject(job.result))
print(result)
