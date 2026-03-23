from django.db import models
from django.contrib.auth.models import User

# --- ĐỊNH NGHĨA CÁC BẢNG TRONG DATABASE ---

# Tin đăng bán hàng
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
    reject_reason = models.TextField(blank=True, null=True) # Lý do Admin từ chối bài (nếu có)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title

# Hình ảnh đi kèm bài đăng (1 bài có thể có nhiều ảnh)
class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listing_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

# Theo dõi biến động giá để vẽ biểu đồ lịch sử 
class PriceHistory(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='price_history')
    old_price = models.DecimalField(max_digits=12, decimal_places=2)
    new_price = models.DecimalField(max_digits=12, decimal_places=2)
    changed_at = models.DateTimeField(auto_now_add=True)

# Báo cáo / Tố cáo vi phạm
class UserReport(models.Model):
    REPORT_STATUS = [
        ('PENDING', 'Chờ xử lý'),          # Mới gửi lên, chưa có Admin nào nhận
        ('RESOLVED', 'Đã xử lý (Vi phạm)'), # Admin chốt vi phạm, hệ thống tự cộng 1 gậy
        ('REJECTED', 'Đã xử lý (Bỏ qua)'), # Admin thấy báo cáo không hợp lệ
    ]
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.TextField() # Nội dung tố cáo là gì
    admin_reply = models.TextField(blank=True, null=True) # Phản hồi chính thức từ Admin
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Report {self.id} on {self.target_user.username}"

# Bằng chứng (ảnh) đi kèm báo cáo
class ReportEvidence(models.Model):
    report = models.ForeignKey(UserReport, on_delete=models.CASCADE, related_name='evidences')
    image = models.ImageField(blank=True, null=True, upload_to='report_evidences/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

# Giao dịch mua bán thành công 
class Transaction(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    amount = models.DecimalField(max_digits=12, decimal_places=2) # Giá bán
    platform_fee = models.DecimalField(max_digits=12, decimal_places=2) # Hoa hồng cho sàn
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Transaction {self.id}"

# Thông tin mở rộng của User: Dùng để khóa nick hoặc đếm số gậy cảnh cáo
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_blocked = models.BooleanField(default=False)
    warning_count = models.IntegerField(default=0)
    block_reason = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return f"Profile of {self.user.username}"

# Snapshot: Lưu lại 'ảnh chụp' số liệu để xem báo cáo theo ngày
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

# Nhật ký thao tác (Audit Log) - Admin nào làm gì là ghi hết vào đây để truy vết
class AdminAuditLog(models.Model):
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=100) # Tên hành động (Vd: Khóa user, Duyệt bài...)
    details = models.TextField(blank=True) # Mô tả chi tiết việc đã làm
    
    # Đối tượng bị tác động (ghi model và id dưới dạng text để linh hoạt)
    target_model = models.CharField(max_length=100, blank=True, null=True)
    target_id = models.CharField(max_length=100, blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.username if self.admin else 'Unknown'} - {self.action} ({self.timestamp})"
