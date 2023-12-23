"""Dataclasses that are used to construct update reports."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class PackageInfo:
    """Dataclass that contains information about a package."""

    package_type: Optional[str]
    package_name: Optional[str]
    new_version: Optional[str]
    old_version: Optional[str]
    update_status: Optional[str]
    repo: Optional[str]

    def add_attributes(self, attrs):
        """Add attributes to the PackageInfo object."""
        for attr_name, attr_value in attrs.items():
            setattr(self, attr_name, attr_value)


@dataclass
class UpdateSection:
    """Dataclass update section."""

    update_type: str
    update_status: bool
    update_details: Dict


@dataclass
class PretendError:
    """Dataclass pretend error."""

    error_type: str
    error_details: List[str]


@dataclass
class PretendSection:
    """Dataclass pretend section."""

    pretend_status: bool
    pretend_details: Optional[PretendError]


@dataclass
class DiskUsageStats:
    """Dataclass disk usage stats."""

    mount_point: str
    total: str
    used: str
    free: str
    percent_used: str


@dataclass
class DiskUsage:
    """Dataclass disk usage."""

    before_update: Optional[List[DiskUsageStats]]
    after_update: Optional[List[DiskUsageStats]]


@dataclass
class LogInfo:
    """Dataclass log info."""

    pretend_emerge: Optional[PretendSection]
    update_system: Optional[UpdateSection]
    disk_usage: DiskUsage
