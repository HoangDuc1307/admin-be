from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework import serializers

from ..models import AdminAuditLog

# Chuyển đổi dữ liệu Log sang JSON để hiển thị lên bảng "Nhật ký hoạt động"
class AdminAuditLogSerializer(serializers.ModelSerializer):
    admin_username = serializers.CharField(source='admin.username', read_only=True)
    target_object = serializers.SerializerMethodField()

    class Meta:
        model = AdminAuditLog
        # Hiển thị các cột: ID, Ai làm, Làm gì, Note chi tiết, Đối tượng nào, Lúc nào
        fields = ['id', 'admin_username', 'action', 'details', 'target_object', 'timestamp']

    def get_target_object(self, obj):
        # Hiển thị tên đối tượng cho dễ hiểu (Ví dụ: Listing #12)
        if obj.target_model and obj.target_id:
            return f"{obj.target_model} #{obj.target_id}"
        return "N/A"

# View quản lý Nhật ký hoạt động
class AdminAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API để Admin xem lại toàn bộ lịch sử thao tác trên hệ thống. 
    Giúp truy vết xem ai đã duyệt bài hoặc khóa user nào.
    """
    queryset = AdminAuditLog.objects.all().order_by('-timestamp')
    serializer_class = AdminAuditLogSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        # Hỗ trợ lọc nhanh theo loại hành động (Ví dụ: chỉ xem log khóa user)
        qs = super().get_queryset()
        action_param = self.request.query_params.get('action')
        if action_param:
            qs = qs.filter(action=action_param)
        return qs
