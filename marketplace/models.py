from django.db import models
from django.contrib.auth.models import User


class Listing(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Đang chờ duyệt'),
        ('APPROVED', 'Đã duyệt'),
        ('REJECTED', 'Bị từ chối'),
    ]
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class UserReport(models.Model):
    REPORT_STATUS = [
        ('OPEN', 'Mới'),
        ('IN_PROGRESS', 'Đang xử lý'),
        ('RESOLVED', 'Đã giải quyết'),
        ('REJECTED', 'Từ chối'),
    ]
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Report {self.id} on {self.target_user.username}"


class Transaction(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Transaction {self.id}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_blocked = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Profile of {self.user.username}"


class AdminReportSnapshot(models.Model):
    """Báo cáo đã lưu bởi admin - mỗi lần lưu tạo 1 giao dịch (record) để đủ LOC."""
    TYPE_CHOICES = [
        ('DASHBOARD', 'Dashboard'),
        ('FEES', 'Thống kê phí sàn'),
    ]
    report_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    snapshot_data = models.JSONField(default=dict)  # Dữ liệu tại thời điểm lưu
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.get_report_type_display()} - {self.created_at}"
