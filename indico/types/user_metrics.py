import datetime
from typing import List

from indico.types.base import BaseType


class AppRoles(BaseType):
    """Info about roles. Name and how many users have this role.

    Attributes:
        role (str): A role name
        count (int): Count of how many users have said role.
    """

    role: str
    count: int


class UserDatasets(BaseType):
    """Dataset Id and roles assigned to user in that dataset.

    Attributes:
        dataset_id (int): The id of a particular dataset
        role (str): A dataset assigned to said dataset.
    """

    dataset_id: int
    role: str


class UserSummaryCounts(BaseType):
    """
    Summary of user counts

    Attributes:
        enabled (int): How many user accounts are enabled.
        disabled (int): How many user accounts are disabled.
    """

    enabled: int
    disabled: int


class UserSnapshot(BaseType):
    """Individual information about a user and their dataset access

    Attributes:
        id (int): The user's id.
        name (str): The user's name.
        email (str): The user's email.
        created_at (str): Time of creation.
        enabled (bool): True if user account is enabled.
        roles (List[str]): List of roles assigned to this user.
        datasets (List[UserDatasets]): List of datasets this user can access.
    """

    id: int
    name: str
    email: str
    created_at: str
    enabled: bool
    roles: List[str]
    datasets: List[UserDatasets]


class UserSummary(BaseType):
    """Summary data on users and app roles

    Attributes:
        users (UserSummarycounts): Counts of enabled/disabled users.
        app_roles (List[AppRoles]): List of all available user roles.
    """

    users: UserSummaryCounts
    app_roles: List[AppRoles]


class DatasetRole(BaseType):
    """Dataset role information

    Attributes:
        dataset_id (int): Id of a particular dataset.
        role (str): Role name which has access to this dataset.
    """

    dataset_id: int
    role: str


class UserChangelog(BaseType):
    """Log entry of a change made to a user's permission

    Attributes:
        id (str): Id of the log entry
        date (datetime): Time of long entry.
        user_id (int): Id of the user whose attributes were changed.
        user_email (str): Email of the user whose attributes were changed.
        updated_by (id): Id of the account which made the change.
        updater_email (str): Email of the account which made the change.
        previously_enabled (bool): True if this account was enabled prior to change.
        enabled (bool): True if account is enabled after the change.
        previous_roles (List[str]): Roles assigned prior to the change.
        roles (List[str]): Roles assigned after the change.
        previous_datasets (List[DatasetRole]): List of dataset/role mappings prior to the change.
        datasets (List[DatasetRole]): List of dataset/role mappings after the change.
        changes_made (List[str]): A list of changed made.

    """

    id: str
    date: datetime
    user_id: int
    user_email: str
    updated_by: int
    updater_email: str
    previously_enabled: bool
    enabled: bool
    previous_roles: List[str]
    roles: List[str]
    previous_datasets: List[DatasetRole]
    datasets: List[DatasetRole]
    changes_made: List[str]


class UserChangelogReport(BaseType):
    """Job id of a request for a changelog report file for download

    Attributes:
        job_id (str): The job id. Use for fetching JobStatus.
    """

    job_id: str
