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
