from indico import IndicoClient, IndicoConfig
from indico.filters import DateRangeFilter, SubmissionFilter, and_, or_
from indico.queries import ListSubmissions

# Create an Indico API client
my_config = IndicoConfig(
    host="try.indico.io", api_token_path="./path/to/indico_api_token.txt"
)
client = IndicoClient(config=my_config)

workflow_id = 5

"""
Example 1
List all submissions that are COMPLETE or FAILED
"""
sub_filter = or_(SubmissionFilter(status="COMPLETE"), SubmissionFilter(status="FAILED"))
submissions = client.call(ListSubmissions(filters=sub_filter))

"""
Example 2
List all submissions that are COMPLETE and FAILED
"""
sub_filter = and_(
    SubmissionFilter(status="COMPLETE"), SubmissionFilter(status="FAILED")
)
submisions = client.call(ListSubmissions(filters=sub_filter))

"""
Example 3
List all submissions that are retrieved and have a filename that contains 'property'
"""
sub_filter = SubmissionFilter(retrieved=True, input_filename="property")
submissions = client.call(ListSubmissions(filters=sub_filter))

"""
Example 4
List all submissions that are created and updated within a certain date range
"""
date_filter = DateRangeFilter(filter_from="2022-01-01", filter_to="2023-01-01")
sub_filter = SubmissionFilter(created_at=date_filter, updated_at=date_filter)

"""
Example 5
List all submissions that are not in progress of being reviewed and are completed
"""
submissions = client.call(
    ListSubmissions(
        filters=SubmissionFilter(status="COMPLETE", review_in_progress=False)
    )
)
