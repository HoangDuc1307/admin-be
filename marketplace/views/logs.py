from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework import serializers

from ..models import AdminAuditLog

# Serializer cho Nhật ký hoạt động: Giúp chuyển đổi dữ liệu log sang JSON để hiển thị ở Frontend
class AdminAuditLogSerializer(serializers.ModelSerializer):
    admin_username = serializers.CharField(source='admin.username', read_only=True)
    target_object = serializers.SerializerMethodField()

    class Meta:
        model = AdminAuditLog
        # Hiển thị các trường: ID, Người thực hiện, Hành động, Chi tiết, Đối tượng liên quan, Thời gian
        fields = ['id', 'admin_username', 'action', 'details', 'target_object', 'timestamp']

    def get_target_object(self, obj):
        """Hàm xử lý hiển thị tên đối tượng bị tác động (Vd: Listing #5)"""
        if obj.target_model and obj.target_id:
            return f"{obj.target_model} #{obj.target_id}"
        return "N/A"

# ViewSet quản trị Nhật ký hoạt động (Audit Log)
class AdminAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API cung cấp nhật ký hoạt động của Admin.
    Dùng để theo dõi vết các thao tác thay đổi dữ liệu.
    """
    queryset = AdminAuditLog.objects.all().order_by('-timestamp')
    serializer_class = AdminAuditLogSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """Hàm hỗ trợ lọc nhật ký theo loại hành động (Filter)"""
        qs = super().get_queryset()
        action_param = self.request.query_params.get('action')
        if action_param:
            qs = qs.filter(action=action_param)
        return qs
