import psutil


class SystemDiagnostics:
    def __init__(self) -> None:
        self.mount_points = self.get_mount_points()
        self.disk_usages = self.get_disk_usage()

    def format_size(self, size):
        """
        Take a size in bytes and return it in a human-readable format.
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if abs(size) < 1024.0:
                return f"{size:3.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}PB"

    def get_mount_points(self):
        """
        Parse /etc/fstab and return a list of mount points.
        """
        mount_points = []
        with open("/etc/fstab", "r") as file:
            for line in file.readlines():
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.split()
                if len(parts) < 2:
                    continue
                if parts[1] == "/tmp" or parts[1] == "swap":
                    continue
                mount_points.append(parts[1])

        return mount_points

    def get_disk_usage(self):
        """
        Get disk usage for the given mount points.
        """
        disk_usages = {}
        for mount_point in self.mount_points:
            try:
                usage = psutil.disk_usage(mount_point)
                disk_usages[mount_point] = {
                    "total": self.format_size(usage.total),
                    "used": self.format_size(usage.used),
                    "free": self.format_size(usage.free),
                    "percent_used": usage.percent,
                }
            except FileNotFoundError:
                print(f"Warning: mount point {mount_point} does not exist.")
            except PermissionError:
                print(
                    f"Warning: no permission to access mount point {mount_point}."
                )
        return disk_usages

    def show_disk_uage(self):
        """
        Print mount point disk usage statistics.
        """
        for mount_point, usage in self.disk_usages.items():
            print(f"Disk usage for {mount_point}:")
            print(f"  Total: {usage['total']}")
            print(f"  Used: {usage['used']}")
            print(f"  Free: {usage['free']}")
            print(f"  Percent used: {usage['percent_used']}%")


if __name__ == "__main__":
    # SystemDiagnostics().show_disk_uage()
    du = SystemDiagnostics().get_disk_usage()
    print(du)
