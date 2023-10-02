from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PackageInfo:
    package_type: str
    package_name: str
    new_version: str
    old_version: str
    update_status: str
    repo: str

    def add_attributes(self, attrs):
        for attr_name, attr_value in attrs.items():
            setattr(self, attr_name, attr_value)


@dataclass
class UpdateSection:
    update_type: str
    update_status: bool
    update_details: Dict[str, PackageInfo]


@dataclass
class PretendError:
    error_type: str
    error_details: List[str]


@dataclass
class PretendSection:
    pretend_status: bool
    pretend_details: PretendError


@dataclass
class DiskUsageStats:
    mount_point: str
    total: str
    used: str
    free: str
    percent_used: str


@dataclass
class DiskUsage:
    before_update: List[DiskUsageStats]
    after_update: List[DiskUsageStats]


@dataclass
class LogInfo:
    pretend_emerge: Optional[PretendSection]
    update_system: Optional[UpdateSection]
    disk_usage: Optional[DiskUsage]


