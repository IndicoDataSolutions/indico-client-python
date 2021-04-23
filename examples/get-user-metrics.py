from datetime import datetime

from indico import IndicoConfig, IndicoClient
from indico.queries.usermetrics import GetUserSummary,GetUserSnapshots
from indico.types.user_metrics import UserSummary

"""
Example 1: User Summary
"""
# Create an Indico API client
my_config = IndicoConfig(
    host="app.indico.io", api_token_path="./path/to/indico_api_token.txt"
)
client = IndicoClient(config=my_config)

user_summary: UserSummary = client.call(GetUserSummary())
print("Wow! there's " + str(user_summary.users.enabled) + " users enabled on the app!")
print("Did you know there are " + str(len(user_summary.app_roles)) + " roles available here?")


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
for snapshot in client.paginate(GetUserSnapshots(date=datetime.now(), user_id=1)):
    snapshots.extend(snapshot)
print("Fetched just " + str(len(snapshots)) + " user for analysis")

