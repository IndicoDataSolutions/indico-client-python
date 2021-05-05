import datetime

from indico.types.base import BaseType
from typing import List


class AppRoles(BaseType):
    """Info about roles. Name and how many users have this role."""
    role: str
    count: int


class UserDatasets(BaseType):
    """Dataset Id and roles assigned to user in that dataset."""
    dataset_id: int
    role: str


class UserSummaryCounts(BaseType):
    """Summary of user counts"""
    enabled: int
    disabled: int


class UserSnapshot(BaseType):
    """Individual information about a user and their dataset access"""
    id: int
    name: str
    email: str
    created_at: str
    enabled: bool
    roles: List[str]
    datasets: List[UserDatasets]


class UserSummary(BaseType):
    """Summary data on users and app roles"""
    users: UserSummaryCounts
    app_roles: List[AppRoles]


class DatasetRole(BaseType):
    """Dataset role information"""
    dataset_id: int
    role: str


class UserChangelog(BaseType):
    """Log entry of a change made to a user's permission"""
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
    """Job id of a request for a changelog report file"""
    job_id: str
