from django.db import models
from django.contrib.auth.models import User

# Định nghĩa các bảng Database
 
# Tin đăng (Listing)
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
    reject_reason = models.TextField(blank=True, null=True) # Lý do từ chối bài
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title

# Ảnh sản phẩm (Một tin có thể có nhiều ảnh)
class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listing_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

# Lịch sử đổi giá (Dùng để vẽ chart)
class PriceHistory(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='price_history')
    old_price = models.DecimalField(max_digits=12, decimal_places=2)
    new_price = models.DecimalField(max_digits=12, decimal_places=2)
    changed_at = models.DateTimeField(auto_now_add=True)

# Báo cáo / Khiếu nại (Report)
class UserReport(models.Model):
    REPORT_STATUS = [
        ('OPEN', 'Mới'),
        ('IN_PROGRESS', 'Đang xử lý'),
        ('RESOLVED', 'Đã giải quyết'),
        ('REJECTED', 'Từ chối'),
    ]
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.TextField() # Lý do tố cáo
    admin_reply = models.TextField(blank=True, null=True) # Phản hồi của Admin
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Report {self.id} on {self.target_user.username}"

# Ảnh bằng chứng cho report
class ReportEvidence(models.Model):
    report = models.ForeignKey(UserReport, on_delete=models.CASCADE, related_name='evidences')
    image = models.ImageField(blank=True, null=True, upload_to='report_evidences/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

# Giao dịch thành công (Transaction)
class Transaction(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    amount = models.DecimalField(max_digits=12, decimal_places=2) # Số tiền
    platform_fee = models.DecimalField(max_digits=12, decimal_places=2) # Phí sàn thu
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Transaction {self.id}"

# Profile phụ: Lưu trạng thái khóa/cảnh cáo user
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_blocked = models.BooleanField(default=False)
    warning_count = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"Profile of {self.user.username}"

# Snapshot: Lưu lại data dashboard (phục vụ thống kê sau này)
class AdminReportSnapshot(models.Model):
    TYPE_CHOICES = [
        ('DASHBOARD', 'Dashboard'),
        ('FEES', 'Thống kê phí sàn'),
    ]
    report_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    snapshot_data = models.JSONField(default=dict)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.get_report_type_display()} - {self.created_at}"

# Nhật ký Admin (Audit Log) để kiểm soát hành động admin
class AdminAuditLog(models.Model):
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=100) # Tên hành động (Vd: Khóa user, Duyệt bài)
    details = models.TextField(blank=True) # Chi tiết nội dung thao tác
    
    # Thông tin về đối tượng bị tác động (ghi dưới dạng文本 cho đơn giản)
    target_model = models.CharField(max_length=100, blank=True, null=True)
    target_id = models.CharField(max_length=100, blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.username if self.admin else 'Unknown'} - {self.action} ({self.timestamp})"
