from indico import IndicoClient
from indico.config.config import IndicoConfig
from indico.queries import ListSubmissions
from indico.filters import SubmissionFilter

devconf = IndicoConfig(
    host="dev.indico.io",
    api_token_path="/home/astha/Downloads/indico_api_token_dev.txt",
)

client = IndicoClient(config=devconf)
_fil = SubmissionFilter(status="PENDING_REVIEW")

subs = client.call(ListSubmissions(filters=_fil))
for s in subs:
    print(s.id, s.workflow_id, s.status)
print("Paginating for {len(subs)}....")

i = 0
for s in client.paginate(ListSubmissions(limit=2, filters=_fil)):
    print(s.id, s.workflow_id, s.status)
    i += 1
    if i > 9:
        break
